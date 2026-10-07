// Admin API for the portfolio site, run as a Cloudflare Worker.
// It checks the admin password, then commits content/*.json and img/* files to the site's GitHub repo
// (GitHub Pages rebuilds the site from that commit). Secrets live in the Worker, never in this repo:
//   ADMIN_PASSWORD  the password typed into /admin
//   SESSION_SECRET  random string used to sign login tokens
//   GITHUB_TOKEN    fine-grained token with "Contents: read and write" on the site repo only

const FILES = { posts: 'content/posts.json', gallery: 'content/gallery.json' };
const SESSION_MS = 12 * 60 * 60 * 1000;
const MAX_UPLOAD_B64 = 9 * 1024 * 1024; // per file, base64 characters
const enc = new TextEncoder();
const failures = new Map(); // best-effort per-isolate brute-force limiter

function cors(env, req) {
  const origin = req.headers.get('Origin') || '';
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map((s) => s.trim()).filter(Boolean);
  const h = { Vary: 'Origin', 'Access-Control-Allow-Headers': 'Authorization, Content-Type', 'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS' };
  if (allowed.includes(origin)) h['Access-Control-Allow-Origin'] = origin;
  return h;
}
const json = (env, req, body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...cors(env, req) } });

async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return new Uint8Array(await crypto.subtle.sign('HMAC', key, enc.encode(msg)));
}
function b64url(bytes) { return btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
function same(a, b) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i];
  return d === 0;
}
async function passwordOk(env, given) {
  const k = 'pw-compare';
  return same(await hmac(k, String(given)), await hmac(k, env.ADMIN_PASSWORD));
}
async function makeToken(env) {
  const exp = String(Date.now() + SESSION_MS);
  return exp + '.' + b64url(await hmac(env.SESSION_SECRET, exp));
}
async function tokenOk(env, req) {
  const m = /^Bearer (\d+)\.([\w-]+)$/.exec(req.headers.get('Authorization') || '');
  if (!m || Number(m[1]) < Date.now()) return false;
  return same(enc.encode(b64url(await hmac(env.SESSION_SECRET, m[1]))), enc.encode(m[2]));
}

async function gh(env, path, init = {}) {
  const r = await fetch('https://api.github.com/repos/' + env.REPO + path, {
    ...init,
    headers: {
      Authorization: 'Bearer ' + env.GITHUB_TOKEN,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'portfolio-admin-worker',
      'X-GitHub-Api-Version': '2022-11-28',
      ...(init.headers || {}),
    },
  });
  return r;
}
async function getFile(env, path) {
  const r = await gh(env, '/contents/' + path + '?ref=' + env.BRANCH);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error('GitHub read failed (' + r.status + ')');
  return r.json();
}
async function putFile(env, path, b64, message, sha) {
  const body = { message, content: b64, branch: env.BRANCH, ...(sha ? { sha } : {}) };
  const r = await gh(env, '/contents/' + path, { method: 'PUT', body: JSON.stringify(body) });
  if (!r.ok) throw new Error('GitHub write failed (' + r.status + ')');
  return r.json();
}
function utf8ToB64(s) {
  const bytes = enc.encode(s);
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}
function b64ToUtf8(b64) {
  const bin = atob(b64.replace(/\n/g, ''));
  return new TextDecoder().decode(Uint8Array.from(bin, (c) => c.charCodeAt(0)));
}

const str = (v, max) => typeof v === 'string' && v.length <= max;
const slug = (v) => str(v, 80) && /^[a-z0-9][a-z0-9-]*$/.test(v);
const imgPath = (v) => str(v, 120) && /^img\/[a-z0-9][a-z0-9._-]*\.(webp|png|jpg|gif)$/.test(v);
const tagsOk = (v) => Array.isArray(v) && v.length <= 30 && v.every((t) => slug(t));
function validate(name, data) {
  if (name === 'gallery') {
    if (!data || !Array.isArray(data.images) || data.images.length > 2000) return 'gallery must be { images: [] }';
    for (const i of data.images) {
      if (!imgPath(i.src) || !str(i.caption ?? '', 300) || !tagsOk(i.tags ?? [])) return 'bad gallery item: ' + String(i && i.src);
    }
    return null;
  }
  if (!data || !Array.isArray(data.posts) || data.posts.length > 500) return 'posts must be { posts: [] }';
  const seen = new Set();
  for (const p of data.posts) {
    if (!slug(p.slug) || seen.has(p.slug)) return 'bad or duplicate slug: ' + String(p && p.slug);
    seen.add(p.slug);
    if (!['brand', 'signs'].includes(p.cat)) return 'bad category on ' + p.slug;
    if (!str(p.title, 200) || !str(p.kicker ?? '', 300) || !str(p.blurb ?? '', 1500)) return 'bad text on ' + p.slug;
    if (!tagsOk(p.tags ?? [])) return 'bad tags on ' + p.slug;
    if (!Array.isArray(p.body) || p.body.length > 60 || !p.body.every((s) => str(s, 8000))) return 'bad body on ' + p.slug;
    for (const k of ['hero', 'cardImg']) if (p[k] && !imgPath(p[k])) return 'bad image path on ' + p.slug;
    for (const t of [...(p.thumbs || []), ...(p.cardThumbs || [])]) if (!imgPath(t.src)) return 'bad image path on ' + p.slug;
  }
  return null;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(env, req) });
    const origin = req.headers.get('Origin');
    if (origin && !cors(env, req)['Access-Control-Allow-Origin']) return json(env, req, { error: 'origin not allowed' }, 403);

    try {
      if (url.pathname === '/api/health') {
        // which secrets this Worker can see (true/false only, never the values)
        return json(env, req, { ADMIN_PASSWORD: !!env.ADMIN_PASSWORD, SESSION_SECRET: !!env.SESSION_SECRET, GITHUB_TOKEN: !!env.GITHUB_TOKEN });
      }

      if (url.pathname === '/api/login' && req.method === 'POST') {
        const ip = req.headers.get('CF-Connecting-IP') || 'x';
        const f = failures.get(ip) || { n: 0, until: 0 };
        if (f.until > Date.now()) return json(env, req, { error: 'Too many attempts. Wait a few minutes.' }, 429);
        const { password } = await req.json().catch(() => ({}));
        if (typeof password === 'string' && (await passwordOk(env, password))) {
          failures.delete(ip);
          return json(env, req, { token: await makeToken(env) });
        }
        f.n += 1;
        if (f.n >= 5) { f.until = Date.now() + 10 * 60 * 1000; f.n = 0; }
        failures.set(ip, f);
        await new Promise((r) => setTimeout(r, 700));
        return json(env, req, { error: 'Wrong password' }, 401);
      }

      if (!url.pathname.startsWith('/api/')) return json(env, req, { error: 'not found' }, 404);
      if (!(await tokenOk(env, req))) return json(env, req, { error: 'Not signed in' }, 401);

      if (url.pathname === '/api/content' && req.method === 'GET') {
        const out = {};
        for (const [name, path] of Object.entries(FILES)) {
          const f = await getFile(env, path);
          out[name] = f ? JSON.parse(b64ToUtf8(f.content)) : name === 'posts' ? { posts: [] } : { images: [] };
        }
        return json(env, req, out);
      }

      const put = /^\/api\/content\/(posts|gallery)$/.exec(url.pathname);
      if (put && req.method === 'PUT') {
        const { data } = await req.json();
        const bad = validate(put[1], data);
        if (bad) return json(env, req, { error: bad }, 400);
        const cur = await getFile(env, FILES[put[1]]);
        await putFile(env, FILES[put[1]], utf8ToB64(JSON.stringify(data, null, 1) + '\n'), 'admin: update ' + put[1], cur && cur.sha);
        return json(env, req, { ok: true });
      }

      if (url.pathname === '/api/upload' && req.method === 'POST') {
        const { name, full, thumb } = await req.json();
        if (!/^[a-z0-9][a-z0-9-]{0,60}\.webp$/.test(name || '')) return json(env, req, { error: 'bad file name' }, 400);
        for (const b of [full, thumb]) if (typeof b !== 'string' || b.length > MAX_UPLOAD_B64 || !/^[A-Za-z0-9+/=]+$/.test(b)) return json(env, req, { error: 'bad image data' }, 400);
        if (await getFile(env, 'img/' + name)) return json(env, req, { error: 'a file with that name exists already' }, 409);
        await putFile(env, 'img/' + name, full, 'admin: add image ' + name);
        await putFile(env, 'img/t/' + name, thumb, 'admin: add thumbnail ' + name);
        return json(env, req, { ok: true, src: 'img/' + name });
      }

      return json(env, req, { error: 'not found' }, 404);
    } catch (e) {
      return json(env, req, { error: String((e && e.message) || e) }, 502);
    }
  },
};
