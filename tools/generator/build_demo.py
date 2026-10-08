"""Builds the offline demo pages from the real site content (no retyping).

    python build_demo.py

Reads the site (content/*.json, img/) and writes *-v2.html, v2.css and v2.js next to this file.
Then publish_to_site.py --live copies them into the site. A GitHub Action runs both whenever content or images change.
"""
import html as H
import json, math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("PORTFOLIO_DIR") or os.path.normpath(os.path.join(HERE, "..", ".."))   # the site (repo root)
PREVIEW = os.environ.get("PREVIEW") == "1"   # offline draft preview: includes drafts/, writes to preview/, never published
REL = "../../ben-wells-design/" if PREVIEW else "../ben-wells-design/"
OUT = os.path.join(HERE, "preview") if PREVIEW else HERE
if PREVIEW:
    os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(HERE, "source-site.html"), encoding="utf-8").read()
posts = json.load(open(os.path.join(SITE, "content", "posts.json"), encoding="utf-8"))["posts"]
HIDDEN = [p["slug"] for p in posts if p.get("hidden")]   # posts switched off in the admin: no card, pin, page or link anywhere
posts = [p for p in posts if not p.get("hidden")]
if PREVIEW:
    posts = json.load(open(os.path.join(HERE, "drafts", "posts.json"), encoding="utf-8")) + posts
else:
    for _f in os.listdir(HERE):
        if _f.startswith("case-") and _f.endswith("-v2.html"):
            os.remove(os.path.join(HERE, _f))   # stale case pages from a previous build
gallery = json.load(open(os.path.join(SITE, "content", "gallery.json"), encoding="utf-8"))["images"]
if PREVIEW:
    gallery = json.load(open(os.path.join(HERE, "drafts", "gallery.json"), encoding="utf-8")) + gallery

# image key -> file path (the site's IMG map)
a = src.index("  var IMG = {")
b = src.index("\n  };", a)
IMG = dict(re.findall(r"^    '([^']+)': '([^']+)',?$", src[a:b], re.M))


def img(p):
    if p.startswith("@draft/"):
        return "../drafts/img/" + p[7:] + ".webp"
    return REL + IMG.get(p, p)


def thumb(p):
    if p.startswith("@draft/"):
        return "../drafts/img/t/" + p[7:] + ".webp"
    p = IMG.get(p, p)
    return REL + ("img/t/" + os.path.splitext(p[4:])[0] + ".webp" if re.match(r"^img/[^/]+$", p) else p)


def e(s):
    return H.escape(s, quote=True)


# ---------- shared css ----------
EXTRA = r'''
  /* ---- inner pages ---- */
  .pagehead { position:relative; background:var(--charcoal); padding:130px 0 56px; border-bottom:1px solid var(--line-soft); overflow:hidden; }
  .pagehead::before { content:""; position:absolute; inset:0; background:url('../ben-wells-design/img/hero_halftone.webp') center 38%/cover; opacity:.22; }
  .pagehead::after { content:""; position:absolute; inset:0; background:linear-gradient(180deg, rgba(23,24,26,.1), var(--charcoal)); }
  .pagehead .wrap { position:relative; z-index:2; }
  .pagehead h1 { font-size:60px; font-weight:900; line-height:.98; letter-spacing:-2px; }
  .pagehead p { font-size:18px; line-height:1.4; color:#c9ccd2; margin-top:18px; max-width:680px; }
  .back { display:inline-block; color:var(--slate); text-decoration:none; font-size:13px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; margin-bottom:22px; }
  .back:hover { color:var(--ink); }
  .section-dark { background:var(--charcoal); padding:60px 0 80px; }
  .section-light { background:var(--grey); color:var(--text); padding:60px 0 80px; }
  .filters { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:34px; }
  .fchip { font:inherit; font-size:12px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:var(--slate); background:transparent; border:1px solid var(--line); border-radius:var(--shape-sm); padding:10px 16px; cursor:pointer; }
  .fchip:hover { color:var(--ink); border-color:var(--slate); }
  .fchip.on { background:var(--red); border-color:var(--red); color:#17181A; }
  .light .fchip { color:#4a4b4d; border-color:#9a9b9e; } .light .fchip.on { color:#17181A; }

  .design-top { display:grid; grid-template-columns:1.3fr 1fr; gap:36px; align-items:start; margin-bottom:56px; }
  .map-box { background:var(--raised); border:1px solid var(--line-soft); border-radius:var(--shape); padding:22px; }
  .map-box h3, .gal-box h3 { font-size:26px; font-weight:800; letter-spacing:-.6px; margin:4px 0 6px; }
  .map-box p, .gal-box p { color:var(--slate); font-size:14px; margin-bottom:14px; }
  .map-box svg { width:100%; height:auto; display:block; }
  .map-box svg path { fill:#26282D; stroke:#34373D; stroke-width:2; }
  .mapwrap { position:relative; }
  .pin { border:0; cursor:pointer; position:absolute; width:14px; height:14px; border-radius:50%; background:var(--red); box-shadow:0 0 0 5px rgba(229,23,31,.25); transform:translate(-50%,-50%); }
  .gal-grid3 { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; margin-bottom:16px; }
  .gal-grid3 a { aspect-ratio:1; overflow:hidden; background:var(--raised2); display:block; border-radius:0; }
  .gal-grid3 img { width:100%; height:100%; object-fit:cover; display:block; transition:transform .25s; }
  .gal-grid3 a:hover img { transform:scale(1.06); }

  .post { display:grid; grid-template-columns:200px 1fr; gap:26px; background:var(--raised); border:1px solid var(--line-soft); border-radius:var(--shape); padding:22px; margin-bottom:18px; }
  .post .ph { aspect-ratio:1; background:var(--raised2); overflow:hidden; display:block; }
  .post .ph.contain { background:var(--card); }
  .post .ph img { width:100%; height:100%; object-fit:cover; display:block; }
  .post .ph.contain img { object-fit:contain; padding:10px; }
  .post h2 { font-size:30px; font-weight:800; letter-spacing:-.8px; line-height:1.05; margin:6px 0 10px; }
  .post p { color:#c9ccd2; font-size:16px; line-height:1.5; margin-bottom:14px; }
  .kick { font-size:11px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--red); }
  .tagrow { display:flex; flex-wrap:wrap; gap:6px 14px; margin-bottom:14px; }
  .tagrow a { color:var(--slate); text-decoration:none; font-size:13px; }
  .tagrow a:hover { color:var(--red); }
  .thumbs { display:flex; gap:8px; margin-bottom:16px; }
  .thumbs img { width:60px; height:46px; object-fit:cover; background:var(--card); }

  .detail { max-width:760px; }
  .detail .hero-img { background:var(--raised); border-radius:var(--shape); overflow:hidden; margin-bottom:34px; }
  .detail .hero-img.contain { background:var(--card); } .detail .hero-img img { display:block; width:100%; height:auto; max-height:560px; object-fit:contain; }
  .detail p { font-size:18px; line-height:1.65; color:#d4d6da; margin-bottom:20px; }
  .detail-gal { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:14px; margin-top:34px; }
  .detail-gal figure { margin:0; } .detail-gal img { width:100%; display:block; background:var(--card); border-radius:0; }
  .detail-gal figcaption { color:var(--slate); font-size:13px; margin-top:6px; }

  .masonry { column-count:4; column-gap:10px; }
  .masonry a { display:block; margin:0 0 10px; break-inside:avoid; background:var(--raised2); position:relative; overflow:hidden; }
  .masonry img { width:100%; display:block; }
  .masonry span { position:absolute; left:0; right:0; bottom:0; padding:22px 10px 8px; font-size:12px; background:linear-gradient(transparent, rgba(23,24,26,.88)); opacity:0; transition:opacity .2s; }
  .masonry a:hover span { opacity:1; }

  .devpost { background:var(--raised); border:1px solid var(--line-soft); border-radius:var(--shape); margin-bottom:34px; overflow:hidden; }
  .devmedia { background:#0e0f11; padding:22px; display:flex; flex-wrap:wrap; gap:14px; justify-content:center; }
  .devmedia video, .devmedia img { max-width:100%; max-height:420px; display:block; }
  .devmedia figure { margin:0; text-align:center; } .devmedia figcaption { font-size:12px; color:var(--slate); margin-top:6px; }
  .devmedia svg { max-width:100%; height:auto; }
  .devbody { padding:30px 34px 34px; }
  .devbody h2 { font-size:38px; font-weight:800; letter-spacing:-1px; margin:6px 0 16px; }
  .devbody p { color:#c9ccd2; font-size:17px; line-height:1.6; margin-bottom:16px; }
  .devbody code { background:var(--raised2); padding:1px 6px; font-size:.9em; }
  .private { display:inline-block; font-size:12px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:var(--slate); border:1px solid var(--line); border-radius:var(--shape-sm); padding:10px 16px; }

  .lede { font-size:22px; line-height:1.5; letter-spacing:-.4px; color:var(--text); max-width:820px; margin-bottom:40px; }
  .items { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
  .item { background:var(--card); border-top:4px solid var(--red); border-radius:var(--shape); padding:32px 30px; color:var(--text); }
  .item h3 { font-size:24px; font-weight:800; letter-spacing:-.5px; margin:8px 0 12px; } .item p { color:var(--body); line-height:1.55; font-size:16px; }
  .item ul { margin:16px 0 0; padding-left:18px; color:var(--body); line-height:1.7; font-size:15px; }
  .rcards { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
  .rcard { background:var(--card); border-radius:var(--shape); padding:34px; color:var(--text); }
  .rcard h3 { font-size:28px; font-weight:800; letter-spacing:-.7px; margin:8px 0 12px; } .rcard p { color:var(--body); line-height:1.55; margin-bottom:22px; }
  .ract { display:flex; align-items:center; gap:22px; flex-wrap:wrap; } .ract a.v { color:var(--text); font-weight:700; }

  .post.flash { animation:flash 1.5s ease; } @keyframes flash { 0%,100%{border-color:var(--line-soft);box-shadow:none} 25%,75%{border-color:var(--red);box-shadow:0 0 0 3px rgba(229,23,31,.25)} }

  /* dev page: each project is laid out like a Steam store page. Media viewer on the left (main view + thumbnail row), project text on the right. */
  .dp { display:grid; grid-template-columns:minmax(0,1.8fr) minmax(0,1fr); gap:22px; max-width:1100px; margin-bottom:64px; align-items:start; }
  .dp-media, .dp-info { min-width:0; }
  .dp-main { background:#000; border-radius:var(--shape); overflow:hidden; aspect-ratio:16 / 9; display:flex; align-items:center; justify-content:center; }
  .dp-main video, .dp-main img { width:100%; height:100%; object-fit:contain; display:block; }
  .dp-svgmain { width:100%; height:100%; display:flex; align-items:center; justify-content:center; padding:18px; background:#0e0f11; }
  .dp-svgmain svg { max-width:100%; max-height:100%; height:auto; }
  .dp-row { margin-top:6px; }
  .dp-thumbs { display:flex; gap:4px; overflow-x:auto; scrollbar-width:none; scroll-behavior:smooth; }
  .dp-thumbs::-webkit-scrollbar { display:none; }
  .dp-tile { flex:0 0 auto; width:118px; height:66px; padding:0; border:2px solid transparent; background:#0e0f11; position:relative; overflow:hidden; cursor:pointer; opacity:.78; transition:opacity .15s ease, border-color .15s ease; }
  .dp-tile:hover { opacity:1; }
  .dp-tile.on { opacity:1; border-color:#e6e9ef; }
  .dp-tile img { width:100%; height:100%; object-fit:cover; display:block; }
  .dp-svgthumb { display:block; width:100%; height:100%; padding:4px; } .dp-svgthumb svg { width:100%; height:100%; display:block; }
  .dp-ic { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); width:28px; height:28px; border-radius:50%; background:rgba(14,16,20,.78); color:#fff; display:flex; align-items:center; justify-content:center; font-size:10px; padding-left:2px; pointer-events:none; border:1px solid rgba(255,255,255,.6); }
  .dp-ctl { display:flex; align-items:center; gap:6px; margin-top:6px; }
  .dp-ctl.idle { opacity:.4; pointer-events:none; }
  .dp-arrow { flex:0 0 auto; width:34px; height:20px; background:#26303c; color:#c9d3df; border:0; cursor:pointer; font-size:16px; line-height:1; border-radius:2px; }
  .dp-arrow:hover { background:#34414f; color:#fff; }
  .dp-slider { flex:1 1 auto; height:12px; background:#1a2230; position:relative; border-radius:2px; }
  .dp-knob { position:absolute; top:0; bottom:0; left:0; width:30%; background:#46576b; border-radius:2px; cursor:grab; }
  .dp-info { background:var(--raised); border:1px solid var(--line-soft); border-radius:var(--shape); padding:22px 22px 20px; display:flex; flex-direction:column; max-height:max(var(--dp-h, 9999px), 260px); }
  .dp.open .dp-info { max-height:none; }
  .dp-text { position:relative; overflow:hidden; flex:1 1 auto; min-height:0; }
  .dp-text.clamped::after { content:""; position:absolute; left:0; right:0; bottom:0; height:56px; pointer-events:none; background:linear-gradient(transparent, var(--raised)); }
  .dp.open .dp-text { overflow:visible; }
  .dp.open .dp-text::after { display:none; }
  .dp-more { align-self:flex-start; margin-top:12px; background:transparent; border:1px solid var(--line); color:var(--ink); font:inherit; font-size:13px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; padding:9px 16px; cursor:pointer; border-radius:var(--shape-sm); }
  .dp-more:hover { background:var(--raised2); border-color:var(--slate); }
  .dp-info h2 { font-size:30px; font-weight:700; letter-spacing:-.6px; line-height:1.1; margin:6px 0 14px; }
  .dp-info p { color:#c9ccd2; font-size:15px; line-height:1.6; margin-bottom:14px; }
  .dp-info code { background:var(--raised2); padding:1px 6px; font-size:.9em; }
  .dp-actions { flex:0 0 auto; margin-top:12px; display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
  @media (max-width:900px) { .dp { grid-template-columns:minmax(0,1fr); } .dp-tile { width:96px; height:54px; } .dp-info h2 { font-size:26px; } }
  .lb { position:fixed; inset:0; background:rgba(14,15,17,.94); z-index:100; display:none; align-items:center; justify-content:center; padding:30px; }
  .lb.open { display:flex; } .lb img { max-width:100%; max-height:100%; object-fit:contain; }
  .lb button { position:absolute; background:var(--raised); color:var(--ink); border:1px solid var(--line); font-size:28px; width:46px; height:60px; cursor:pointer; }
  .lb .x { top:20px; right:20px; height:46px; } .lb .p { left:20px; top:50%; } .lb .n { right:20px; top:50%; }
  .lb figcaption { position:absolute; bottom:18px; left:0; right:0; text-align:center; color:var(--slate); font-size:14px; }
  @media (max-width:900px) {
    .pagehead { padding:110px 0 40px; } .pagehead h1 { font-size:40px; }
    .design-top, .items, .rcards { grid-template-columns:1fr; } .post { grid-template-columns:1fr; } .masonry { column-count:2; }
    .devbody { padding:22px; } .devbody h2 { font-size:30px; }
  }
'''



OVERRIDE = r"""
  /* ---- contrast fixes (checked against WCAG AA: 4.5:1 text, 3:1 large) ---- */
  .btn { color:#fff; } .btn.light { color:var(--red); background:#fff; }
  .chip { background:#e6e7e9; color:#1d1e20; }
  .fchip.on, .light .fchip.on { color:#fff; }
  .kick { color:#ff5a62; }
  .bar nav a[style] { color:#ff5a62 !important; }
  .trusted h4 { color:var(--text); }
  .trusted .label, .services .label, .process .label, .section-light .label, .section-light .kick, .item .kick, .rcard .kick { color:#38393b; }
  .svc small, .step small, .item .kick, .rcard .kick, .section-light .kick { color:#7d0b11; }
  .services .label, .process .label, .section-light .label { color:#2a2b2d; }
  .cta .kick { color:#fff; opacity:1 !important; }
  /* case-study images sit on white, not dark */
  .post .ph, .post .ph.contain, .shot, .shot.contain, .detail .hero-img, .detail .hero-img.contain, .detail-gal img, .thumbs img { background:#fff; }
  .detail-gal figure a { display:block; background:#fff; }
  .gal-track a, .masonry a { background:#fff; }
  /* extrude layering: the bright red text is always the top layer. The sheen overlay is a copy of the text sitting ABOVE it, so it must not inherit the dark-red extrusion shadows (they would paint over the red face). */
  .pagehead .gh-cta { position:absolute; right:0; top:50%; transform:translateY(-50%); margin:0; }
  @media (max-width:900px) { .pagehead .gh-cta { position:static; transform:none; margin-top:22px; } }
  .design-top[hidden] { display:none !important; }
  .post.f-hide, .post.pg-hide { display:none !important; }
  .more-wrap { text-align:center; margin:30px 0 10px; }
  .more-wrap[hidden] { display:none; }
  .fx::after, .stat-card b::after, .build-word::after, .results-grid b::after { text-shadow:none !important; }
  /* full-width map panel + one-row endless gallery strip */
  .design-top { display:block; margin-bottom:44px; }
  .map-box { width:100%; }
  /* the map fills the whole panel, proportionally: it covers the frame and is cropped where it overflows; the heading sits on top */
  .map-box { position:relative; overflow:hidden; container-type:size; height:clamp(340px, 42vw, 520px); padding:0; border:0; outline:1px solid var(--line-soft); outline-offset:-1px; }
  .map-box > .label, .map-box > h3, .map-box > p { position:relative; z-index:2; margin-left:24px; margin-right:24px; }
  .map-box > .label { display:block; padding-top:22px; }
  .map-box::after { content:""; position:absolute; inset:0; z-index:1; pointer-events:none; background:linear-gradient(90deg, rgba(21,25,32,.9) 0%, rgba(21,25,32,.5) 30%, rgba(21,25,32,0) 55%); }
  .mapwrap { position:absolute; inset:0; margin:0; width:auto; aspect-ratio:auto; overflow:visible; z-index:0; }
  .mapzoom { position:absolute; left:50%; top:50%; width:calc(max(100cqw, 100cqh * 1.3884) * 1.45); aspect-ratio:603.1 / 434.4; transform:translate(-52%, -47%); }   /* zoomed in on Michigan; the frame stays the same size */
  .mapzoom svg { position:absolute; inset:0; width:100%; height:100%; }
  .pin { z-index:3; }
  .map-shade { position:absolute; inset:0; pointer-events:none; background:linear-gradient(90deg, rgba(21,25,32,.9) 0%, rgba(21,25,32,.5) 30%, rgba(21,25,32,0) 55%); }
  .map-box::after { content:none; }
  /* pins: glow on hover, a tooltip with the job name, click opens that job's post */
  a.pin { display:block; text-decoration:none; transition:box-shadow .15s ease, background .15s ease; }
  a.pin::before { content:""; position:absolute; inset:-9px; border-radius:50%; }
  a.pin:hover, a.pin:focus-visible { z-index:9; background:#ff3b44; outline:none; box-shadow:0 0 0 5px rgba(255,59,68,.4), 0 0 22px 9px rgba(255,59,68,.65); }
  .pin-tip { position:absolute; left:50%; bottom:calc(100% + 14px); transform:translateX(-50%); white-space:nowrap; pointer-events:none; opacity:0; transition:opacity .15s ease;
    background:#0b0d10; color:#fff; border:1px solid #7a0c11; border-radius:0 10px 0 10px; padding:8px 13px; font-size:13px; font-weight:700; line-height:1.25; text-align:left; box-shadow:0 8px 22px rgba(0,0,0,.5); }
  .pin-tip small { display:block; font-size:11px; font-weight:600; color:#9aa0aa; margin-top:2px; }
  a.pin:hover .pin-tip, a.pin:focus-visible .pin-tip { opacity:1; }
  /* a dot that stands for several jobs in the same area: a count, and a list on hover / tap */
  .pin-multi { width:22px; height:22px; display:flex; align-items:center; justify-content:center; cursor:pointer; background:var(--red); border-radius:50%; box-shadow:0 0 0 5px rgba(229,23,31,.25); transition:box-shadow .15s ease, background .15s ease; }
  .pin-count { font:800 12px/1 Archivo, Arial, sans-serif; color:#fff; pointer-events:none; }
  .pin-multi:hover, .pin-multi:focus-visible, .pin-multi.open { z-index:9; background:#ff3b44; outline:none; box-shadow:0 0 0 5px rgba(255,59,68,.4), 0 0 22px 9px rgba(255,59,68,.65); }
  .pin-list { display:none; }
  .pin-pop { position:absolute; z-index:12; width:max-content; max-width:min(300px, calc(100% - 20px)); max-height:calc(100% - 20px); overflow:auto; text-align:left;
    background:#151920; border:1px solid #2a313b; border-radius:0 14px 0 14px; padding:12px 14px; box-shadow:0 14px 34px rgba(0,0,0,.55); }
  .pin-pop[hidden] { display:none; }
  .pin-pop strong { display:block; font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:#9aa0aa; margin-bottom:6px; }
  .pin-pop a { display:flex; justify-content:space-between; align-items:baseline; gap:14px; padding:6px 0; color:#fff; text-decoration:none; font:700 13px/1.25 Archivo, Arial, sans-serif; border-top:1px solid #232933; }
  .pin-pop a:hover, .pin-pop a:focus-visible { color:#ff5a62; outline:none; }
  .pin-pop small { font-size:11px; font-weight:600; color:#9aa0aa; white-space:nowrap; }
  .gal-head { display:flex; justify-content:space-between; align-items:flex-end; gap:20px; flex-wrap:wrap; margin-bottom:18px; }
  .gal-head h3 { font-size:26px; font-weight:700; letter-spacing:-.5px; margin:4px 0 6px; } .gal-head p { color:var(--slate); font-size:14px; }
  .gal-strip { overflow:hidden; margin-bottom:56px; -webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent); mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent); }
  .gal-track { display:flex; gap:8px; width:max-content; animation:gal-scroll var(--gal-dur,220s) linear infinite; }
  .gal-strip:hover .gal-track, .gal-strip:focus-within .gal-track { animation-play-state:paused; }
  .gal-track a { flex:0 0 auto; height:133px; background:var(--raised2); display:block; }
  .gal-track img { height:100%; width:100%; object-fit:cover; display:block; }
  @keyframes gal-scroll { from { transform:translateX(0); } to { transform:translateX(-50%); } }
"""

NIGHT = r"""
  /* ================= NIGHT THEME: dark, low-glare, understated ================= */
  :root {
    --charcoal:#0e1014; --raised:#151920; --raised2:#1b2028; --line:#2a313b; --line-soft:#1d222a;
    --slate:#8b94a3; --ink:#d6dae1; --red:#E5171F; --red-deep:#B4121A; --accent:#E5171F; --accent-text:#ff5a62;
    --grey:#12151a; --grey2:#14181e; --card:#191d24; --text:#d6dae1; --body:#a3acba; --extrude:#2c1215;
  }
  body { background:var(--charcoal); color:var(--ink); }
  h1,h2,h3,h4 { color:var(--ink); }
  .hero h1 { font-weight:700; letter-spacing:-.6px; } .hero h2, .results h2 { font-weight:700; letter-spacing:-.4px; }
  .services h2, .process h2, .pagehead h1, .cta h2, .row h3 { font-weight:700; letter-spacing:-.8px; }
  .pagehead h1 { letter-spacing:-1px; } .process h2 { text-transform:none; }
  .svc h3, .step h3, .item h3, .rcard h3, .devbody h2, .post h2 { font-weight:700; }
  .hero::before { opacity:.22; } .pagehead::before { opacity:.12; }
  .hero::after { background:linear-gradient(180deg, rgba(14,16,20,.35), var(--charcoal)); }
  .red, .hero h1 .red { color:var(--accent); }
  .btn, .btn.lg, .btn.md { background:var(--red); color:#fff; font-weight:700; letter-spacing:.01em; }
  .btn:hover { background:var(--red-deep); color:#fff; }
  .btn.ghost { background:transparent; border:1px solid var(--line); color:var(--ink); } .btn.ghost:hover { background:var(--raised2); }
  .btn.light { background:#fff; color:var(--red); border:0; } .btn.light:hover { background:#f1f1f1; color:var(--red-deep); }
  .row-btn { font-weight:600; color:#e4e7ec; border:1px solid var(--line-soft); }
  .row-btn.design { background:linear-gradient(120deg,#E5171F,#B4121A); }
  .row-btn.dev { background:linear-gradient(120deg,#1f2a38,#18212c); }
  .row-btn.about { background:linear-gradient(120deg,#23272d,#1a1d22); }
  .stat-card { background:var(--raised); border:1px solid var(--line-soft); }
  .stat-card b { color:var(--accent); font-weight:700; } .stat-card span { color:#b3bac6; }
  .stat-card b::after { background:linear-gradient(110deg, transparent 38%, rgba(255,255,255,.45) 50%, transparent 62%) 160% 0 / 260% 100% no-repeat; -webkit-background-clip:text; background-clip:text; }
  .label { color:var(--slate); } .kick, .svc small, .step small, .item .kick, .rcard .kick, .section-light .kick { color:var(--accent-text); }
  .services .label, .process .label, .section-light .label, .trusted .label { color:var(--slate); }
  .bar nav a[style] { color:var(--accent-text) !important; }
  .bar .logo { filter:brightness(.92); }
  /* the carousel keeps a calm, neutral mid-grey so every logo PNG stays readable */
  .trusted { background:#b9bec6; color:#1c1f24; } .trusted h4 { color:#1c1f24; }
  .strip-track img { filter:none; }
  .services, .process, .section-light { background:var(--grey); color:var(--ink); border-top:1px solid var(--line-soft); }
  .process { background:var(--grey2); }
  .svc, .step, .item, .rcard, .chips { background:var(--card); border:1px solid var(--line-soft); color:var(--ink); }
  .svc { border-top:4px solid var(--red); } .item { border-top:4px solid var(--red); }
  .svc p, .step p, .item p, .rcard p, .item ul, .lede, .results-grid p { color:var(--body); }
  .lede { color:#b9c0cc; } .chips h4 { color:var(--ink); }
  .chip { background:#222831; color:#c9ced8; border:1px solid var(--line-soft); }
  .shot, .shot.contain, .post .ph, .post .ph.contain, .detail .hero-img, .detail .hero-img.contain { background:#fff; }
  .work { background:var(--raised); } .post, .devpost { background:var(--raised); }
  .cta { background:var(--red); color:#fff; } .cta .kick { color:#fff; } .cta p { color:#fff; } .cta h2 { color:#fff; }
  .fchip { color:var(--slate); } .fchip.on, .light .fchip.on { background:var(--red); border-color:var(--red); color:#fff; }
  .pin { background:var(--red); box-shadow:0 0 0 5px rgba(229,23,31,.25); }
  footer { background:#0b0d10; }

  /* section headings: on hover the text lifts up-left, a dark extrusion fills back to where it started, one quick sheen */
  @media (hover:hover) {
    .fx { position:relative; display:inline-block; max-width:100%; transition:transform .16s ease-out, text-shadow .16s ease-out; }
    .fx:hover { transform:translate(-4px,-4px); text-shadow:1px 1px 0 #8f0f15, 2px 2px 0 #7a0c11, 3px 3px 0 #660a0e, 4px 4px 0 #52080b; }
    .fx::after { content:attr(data-text); position:absolute; inset:0; pointer-events:none; opacity:0; white-space:normal;
      background:linear-gradient(110deg, transparent 38%, rgba(255,255,255,.5) 50%, transparent 62%) 160% 0 / 260% 100% no-repeat;
      -webkit-background-clip:text; background-clip:text; color:transparent; -webkit-text-fill-color:transparent; }
    .fx:hover::after { opacity:1; animation:sheen .5s ease-out 1; }
  }
  @media (prefers-reduced-motion: reduce) { .fx:hover::after { animation:none; opacity:0; } }
"""

open(os.path.join(HERE, "v2.js"), "w", encoding="utf-8").write("""(function () {
  document.querySelectorAll('.stat-card b').forEach(function (b) { b.setAttribute('data-text', b.textContent); });
  document.querySelectorAll('.pagehead h1, .hero h2, .services h2, .process h2, .cta h2, .row h3').forEach(function (h) {
    if (h.children.length) return; h.classList.add('fx'); h.setAttribute('data-text', h.textContent);
  });
})();
""")

open(os.path.join(HERE, "v2.css"), "w", encoding="utf-8").write(open(os.path.join(HERE, "v2.base.css"), encoding="utf-8").read() + EXTRA + OVERRIDE + NIGHT)

open(os.path.join(HERE, "v2.js"), "a", encoding="utf-8").write("""
(function () {
  var box = document.querySelector('.map-box'), multi = document.querySelectorAll('.pin-multi');
  if (!box || !multi.length) return;
  var pop = document.createElement('div'), cur = null, timer = null;
  pop.className = 'pin-pop'; pop.hidden = true; box.appendChild(pop);
  function place(m) {
    var b = box.getBoundingClientRect(), r = m.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight, gap = 16;
    var x = r.right - b.left + gap;
    if (x + w > b.width - 10) x = r.left - b.left - gap - w;          // not enough room on the right: open to the left
    x = Math.max(10, Math.min(x, b.width - w - 10));
    var y = (r.top + r.height / 2 - b.top) - h / 2;
    y = Math.max(10, Math.min(y, b.height - h - 10));
    pop.style.left = x + 'px'; pop.style.top = y + 'px';
  }
  function open(m) {
    clearTimeout(timer);
    if (cur && cur !== m) cur.classList.remove('open');
    cur = m; m.classList.add('open');
    pop.innerHTML = m.querySelector('.pin-list').innerHTML; pop.hidden = false; place(m);
  }
  function close() { if (cur) cur.classList.remove('open'); cur = null; pop.hidden = true; }
  function later() { clearTimeout(timer); timer = setTimeout(close, 180); }
  multi.forEach(function (m) {
    m.addEventListener('mouseenter', function () { open(m); });
    m.addEventListener('focus', function () { open(m); });
    m.addEventListener('mouseleave', later);
    m.addEventListener('click', function (e) { e.stopPropagation(); if (cur === m && !pop.hidden && e.detail > 0 && matchMedia('(hover: none)').matches) close(); else open(m); });
  });
  pop.addEventListener('mouseenter', function () { clearTimeout(timer); });
  pop.addEventListener('mouseleave', later);
  document.addEventListener('click', function (e) { if (cur && !pop.contains(e.target) && !cur.contains(e.target)) close(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  window.addEventListener('resize', function () { if (cur) place(cur); });
})();
(function () {
  // posts switched off in the admin disappear straight away, even before the pages are rebuilt
  fetch('/content/posts.json?t=' + Date.now(), { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
    if (!d || !d.posts) return;
    d.posts.forEach(function (p) {
      if (!p.hidden) return;
      var path = '/case/' + p.slug + '/';
      if (location.pathname.indexOf(path) === 0) { location.replace('/design/'); return; }
      document.querySelectorAll('a[href="' + path + '"]').forEach(function (a) {
        var box = a.closest('article.post, .pin-list > a, a.pin, .feat, .item, .card') || a; box.style.display = 'none'; box.setAttribute('data-gone', '1');
      });
    });
    document.dispatchEvent(new Event('posts-hidden'));
  }).catch(function () {});
})();
(function () {
  var bar = document.querySelector('.bar'), bands = document.querySelectorAll('.hero, .pagehead'), tick = false;
  function update() {
    tick = false;
    var y = window.pageYOffset || document.documentElement.scrollTop || 0;
    if (bar) bar.classList.toggle('scrolled', y > 8);
    var pf = document.querySelector('.pfx'); if (pf) pf.style.setProperty('--pfy', (-Math.min(y * 0.18, 220)) + 'px');
    for (var i = 0; i < bands.length; i++) bands[i].style.setProperty('--py', Math.min(Math.max(y, 0) * 0.35, 150) + 'px');
  }
  window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(update); } }, { passive: true });
  window.addEventListener('resize', update);
  update();
})();
(function () {
  var bar = document.querySelector('.bar'), btn = document.querySelector('.burger');
  if (!bar || !btn) return;
  var seen = false;
  try { seen = !!localStorage.getItem('menu-seen'); } catch (e) {}
  function set(open) {
    if (open && !seen) { bar.classList.add('first'); seen = true; try { localStorage.setItem('menu-seen', '1'); } catch (e) {} }
    else if (open) bar.classList.remove('first');
    bar.classList.toggle('open', open); btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  btn.addEventListener('click', function (e) { e.stopPropagation(); set(!bar.classList.contains('open')); });
  document.addEventListener('click', function (e) { if (bar.classList.contains('open') && !bar.querySelector('nav').contains(e.target)) set(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
  window.addEventListener('resize', function () { if (innerWidth > 700) set(false); });
})();
(function () {
  // main videos play (muted, looping) while they are on screen and pause when they leave; swapped out of the viewer they pause too
  function start(v) { if (!v.src && v.dataset.src) v.src = v.dataset.src; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  var vids = [].slice.call(document.querySelectorAll('.dp-main video'));
  if (vids.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) start(e.target); else e.target.pause(); }); }, { threshold: 0.5 });
    vids.forEach(function (v) { io.observe(v); });
  } else { vids.forEach(start); }

  // lock each project's text panel to the height of the main video; "Read more" opens it to its full length when the text is longer
  document.querySelectorAll('.dp').forEach(function (dp) {
    var main = dp.querySelector('.dp-main'), text = dp.querySelector('.dp-text'), more = dp.querySelector('.dp-more');
    if (!main || !text || !more) return;
    function fit() {
      dp.style.setProperty('--dp-h', main.getBoundingClientRect().height + 'px');
      if (dp.classList.contains('open')) { more.hidden = false; return; }
      var over = text.scrollHeight > text.clientHeight + 2;
      text.classList.toggle('clamped', over); more.hidden = !over;
    }
    more.addEventListener('click', function () {
      var open = dp.classList.toggle('open');
      more.setAttribute('aria-expanded', open ? 'true' : 'false'); more.textContent = open ? 'Show less' : 'Read more';
      if (!open) { fit(); dp.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
    });
    if ('ResizeObserver' in window) new ResizeObserver(fit).observe(main);
    window.addEventListener('resize', fit); window.addEventListener('load', fit); fit();
  });

  // Steam-style viewer: click a thumbnail to show it in the main view; arrows and the slider move the thumbnail row
  document.querySelectorAll('.dp-media').forEach(function (m) {
    var main = m.querySelector('.dp-main'), strip = m.querySelector('.dp-thumbs');
    if (!strip) return;
    var tiles = [].slice.call(strip.querySelectorAll('.dp-tile')), video = main.querySelector('video');
    tiles.forEach(function (t) {
      t.addEventListener('click', function () {
        tiles.forEach(function (x) { x.classList.toggle('on', x === t); });
        var type = t.dataset.type;
        if (type === 'video') { if (video) main.replaceChildren(video); }
        else if (type === 'img') { var i = document.createElement('img'); i.src = t.dataset.src; i.alt = t.dataset.alt || ''; main.replaceChildren(i); }
        else if (type === 'svg') { var d = document.createElement('div'); d.className = 'dp-svgmain'; d.appendChild(t.querySelector('template').content.cloneNode(true)); main.replaceChildren(d); }
      });
    });
    var knob = m.querySelector('.dp-knob'), slider = m.querySelector('.dp-slider');
    function sync() {
      var max = strip.scrollWidth - strip.clientWidth;
      var ctl = m.querySelector('.dp-ctl');
      if (max <= 1) { ctl.classList.add('idle'); knob.style.width = '100%'; knob.style.left = '0'; return; }
      ctl.classList.remove('idle');
      var ratio = strip.clientWidth / strip.scrollWidth, w = Math.max(16, ratio * 100);
      knob.style.width = w + '%'; knob.style.left = (strip.scrollLeft / max) * (100 - w) + '%';
    }
    strip.addEventListener('scroll', sync); window.addEventListener('resize', sync); sync();
    m.querySelectorAll('.dp-arrow').forEach(function (b) {
      b.addEventListener('click', function () { strip.scrollBy({ left: Number(b.dataset.dir) * 3 * 122, behavior: 'smooth' }); });
    });
    var drag = null;
    knob.addEventListener('pointerdown', function (e) { drag = { x: e.clientX, left: strip.scrollLeft }; knob.setPointerCapture(e.pointerId); strip.style.scrollBehavior = 'auto'; });
    knob.addEventListener('pointermove', function (e) {
      if (!drag) return;
      var max = strip.scrollWidth - strip.clientWidth, track = slider.clientWidth - knob.clientWidth;
      strip.scrollLeft = drag.left + ((e.clientX - drag.x) / Math.max(1, track)) * max;
    });
    knob.addEventListener('pointerup', function () { drag = null; strip.style.scrollBehavior = ''; });
  });
})();
""")

NAV = [("Design", "design-v2.html"), ("About", "about-v2.html"), ("Resume", "resume-v2.html"), ("Dev", "dev-v2.html")]


def page(title, body, active="", extra_js=""):
    nav = "".join('<a href="%s"%s>%s</a>' % (u, ' style="color:var(--red)"' if n == active else "", n) for n, u in NAV)
    return '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>%s</title><link rel="icon" href="../ben-wells-design/favicon.ico" sizes="any" /><link rel="icon" type="image/png" sizes="32x32" href="../ben-wells-design/img/favicon-32.png" /><link rel="apple-touch-icon" href="../ben-wells-design/img/apple-touch-icon.png" /><meta name="description" content="Graphic design portfolio &mdash; logos, brand systems, apparel graphics, and print work. Available for freelance and full-time work." />
<link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&display=swap" />
<link rel="stylesheet" href="v2.css" /></head><body>
<header class="bar"><div class="wrap"><a href="index-v2.html" style="text-decoration:none;color:inherit"><b><img class="logo" src="../ben-wells-design/img/logo.png" alt="Benjamin Wells logo mark" /><span class="nm">Benjamin Wells</span></b></a><nav id="sitenav">%s</nav><button class="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="sitenav"><span></span><span></span><span></span></button></div></header>
%s
<footer><div class="wrap"><span>&copy; 2026 Benjamin Wells</span><span><a href="index-v2.html" style="color:inherit">Home</a> &middot; Graphic Design + Physical Sign Design</span></div></footer>
<div class="lb" id="lb"><button class="x" aria-label="Close">&times;</button><button class="p" aria-label="Previous">&lsaquo;</button><button class="n" aria-label="Next">&rsaquo;</button><figure style="margin:0;display:contents"><img id="lbimg" alt="" /><figcaption id="lbcap"></figcaption></figure></div>
<script src="v2.js"></script>
<script>
(function () {
  var items = [].slice.call(document.querySelectorAll('[data-lb]')), i = 0, lb = document.getElementById('lb');
  function show() { document.getElementById('lbimg').src = items[i].getAttribute('data-lb'); document.getElementById('lbcap').textContent = items[i].getAttribute('data-cap') || ''; }
  items.forEach(function (a, k) { a.addEventListener('click', function (ev) { ev.preventDefault(); i = k; show(); lb.classList.add('open'); }); });
  lb.querySelector('.x').onclick = function () { lb.classList.remove('open'); };
  lb.querySelector('.p').onclick = function () { i = (i + items.length - 1) %% items.length; show(); };
  lb.querySelector('.n').onclick = function () { i = (i + 1) %% items.length; show(); };
  document.addEventListener('keydown', function (ev) { if (!lb.classList.contains('open')) return; if (ev.key === 'Escape') lb.classList.remove('open'); if (ev.key === 'ArrowLeft') lb.querySelector('.p').click(); if (ev.key === 'ArrowRight') lb.querySelector('.n').click(); });
})();
%s
</script></body></html>
''' % (e(title + ' | Benjamin Wells Design'), nav, body, extra_js)


def head(label, title, sub=""):
    # no "Home" link (the logo does that) and no small label above the title (the title says the same thing); case pages keep their kicker line, which carries the project type and date
    lab = ('<span class="label">%s</span>' % label) if label else ""
    return '<section class="pagehead"><div class="wrap">%s<h1>%s</h1>%s</div></section>' % (lab, title, ("<p>%s</p>" % sub) if sub else "")


def tag_links(tags):
    return '<div class="tagrow">%s</div>' % "".join('<a href="gallery-v2.html#%s">#%s</a>' % (t, t) for t in tags)


def write(name, content):
    if PREVIEW:
        content = content.replace('href="v2.css"', 'href="../v2.css"').replace('src="v2.js"', 'src="../v2.js"')
        content = content.replace('../ben-wells-design/', '../../ben-wells-design/').replace('href="index-v2.html"', 'href="../index-v2.html"')
        banner = '<div style="position:fixed;left:0;right:0;bottom:0;z-index:99;background:#e5171f;color:#fff;font:700 13px/1 Archivo,Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;text-align:center;padding:9px 12px">Draft preview &mdash; not on the live site</div>'
        content = content.replace("</body>", banner + "</body>", 1)
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(content)


def _wide(rel):
    """True when an image is far from square, so a square card should show it whole instead of cropping it."""
    try:
        from PIL import Image
        with Image.open(os.path.join(HERE, "drafts", "img", rel[7:] + ".webp") if rel.startswith("@draft/") else os.path.join(SITE, rel)) as im:
            r = im.size[0] / im.size[1]
        return r > 1.6 or r < 0.6
    except Exception:
        return False


# ---------- design page ----------
mapm = re.search(r'<svg class="mi-map-svg".*?</svg>', src, re.S)
pins = re.findall(r'class="mi-pin" style="left:([\d.]+)%; top:([\d.]+)%;" data-target="([^"]+)" title="([^"]+)"', src)
map_svg = re.sub(r'preserveAspectRatio="[^"]*"', 'preserveAspectRatio="xMidYMid meet"', mapm.group(0).replace(' aria-hidden="true"', "")) if mapm else ""
def _geo_xy(lat, lng):
    """Map position (in % of the svg) for a latitude and longitude, calibrated on the Michigan outline in the svg."""
    x = 245 + (lng + 86.82) * 33.3
    y = 98 + (45.86 - lat) * 47.6
    return x / 603.1 * 100, y / 434.4 * 100


def _pin(l, t, slug, title, place):
    return ('<a class="pin" style="left:%.2f%%;top:%.2f%%" href="case-%s-v2.html" aria-label="%s">'
            '<span class="pin-tip">%s<small>%s</small></span></a>') % (l, t, slug, e(title + (" - " + place if place else "")), e(title), e(place))


# every job sits at its real coordinates. Jobs whose dots would overlap at this zoom (the Lansing area: DeWitt, Lansing,
# East Lansing) share ONE dot with a count; hovering or tapping it lists each job and its town.
_pts = []
for _p in posts:
    if _p.get("geo"):
        _x, _y = _geo_xy(*_p["geo"])
        _pts.append({"x": _x, "y": _y, "post": _p})
_clusters = []
for _pt in _pts:
    for _c in _clusters:
        if math.hypot(_c["x"] - _pt["x"], (_c["y"] - _pt["y"]) * 434.4 / 603.1) < 1.6:
            _c["items"].append(_pt)
            _c["x"] = sum(i["x"] for i in _c["items"]) / len(_c["items"])
            _c["y"] = sum(i["y"] for i in _c["items"]) / len(_c["items"])
            break
    else:
        _clusters.append({"x": _pt["x"], "y": _pt["y"], "items": [_pt]})


def _cluster_html(c):
    its = c["items"]
    if len(its) == 1:
        p = its[0]["post"]
        return _pin(c["x"], c["y"], p["slug"], p["title"], p.get("place", ""))
    places = sorted({i["post"].get("place", "") for i in its})
    lst = "".join('<a href="case-%s-v2.html">%s<small>%s</small></a>' % (i["post"]["slug"], e(i["post"]["title"]), e(i["post"].get("place", "")))
                  for i in sorted(its, key=lambda i: (i["post"].get("place", ""), i["post"]["title"])))
    return ('<div class="pin pin-multi" style="left:%.2f%%;top:%.2f%%" tabindex="0" role="group" aria-label="%d projects around %s">'
            '<span class="pin-count">%d</span><span class="pin-list"><strong>%d projects in this area</strong>%s</span></div>'
            % (c["x"], c["y"], len(its), e(" / ".join(places)), len(its), len(its), lst))


pin_html = '<div class="map-shade"></div>' + "".join(_cluster_html(c) for c in _clusters)
teaser = "".join('<a href="gallery-v2.html" style="width:%dpx"><img src="%s" alt="%s" loading="lazy" /></a>' % (round(133 * g["w"] / g["h"]) if g.get("w") and g.get("h") else 175, thumb(g["src"]), e(g.get("caption", ""))) for g in gallery)

# ---- design page filter: the 10 most-used hashtags, with similar tags counted as one ----
_ALIAS = {   # tags that mean the same thing as another (after dropping a trailing "s" / "ing")
    "logo": "brand", "brand-guide": "brand", "banner": "sign", "yard-sign": "sign", "ground-sign": "sign",
    "exterior-sign": "sign", "interior-sign": "sign", "mmd-sign": "sign", "channel-letter": "sign", "marquee": "sign",
    "screen-print": "apparel", "podcast": "broadcast", "flyer": "print", "notebook": "print",
}
_LABEL = {"brand": "branding", "sign": "signs", "vehicle-graphic": "vehicle-graphics", "sticker": "stickers", "school": "schools"}


def _canon(tag):
    t = tag.lower().lstrip("#").strip()
    t = re.sub(r"(ing|s)$", "", t) if len(t) > 4 else t
    return _ALIAS.get(t, t)


_group_posts, _group_gallery = {}, {}
for _p in posts:
    for _g in {_canon(t) for t in _p.get("tags", [])}:
        _group_posts.setdefault(_g, set()).add(_p["slug"])
for _im in gallery:
    for _g in {_canon(t) for t in _im.get("tags", [])}:
        _group_gallery[_g] = _group_gallery.get(_g, 0) + 1
_top = sorted(_group_posts, key=lambda g: (-len(_group_posts[g]), -_group_gallery.get(g, 0), g))[:10]
_post_groups = {p["slug"]: " ".join(g for g in _top if p["slug"] in _group_posts[g]) for p in posts}
_chips = "".join('<button class="fchip" data-f="%s">#%s</button>' % (g, _LABEL.get(g, g)) for g in _top)
print("filter tags:", [(_LABEL.get(g, g), len(_group_posts[g])) for g in _top])

cards = []
for p in posts:
    th = "".join('<img src="%s" alt="" />' % thumb(t["src"]) for t in p.get("cardThumbs", [])[:3])
    contain = " contain" if p.get("cardFit") != "cover" and (p["cardImg"].endswith(".png") or "lockup" in p["cardImg"] or _wide(p["cardImg"])) else ""
    cards.append('''<article class="post" id="post-%s" data-cat="%s" data-tags="%s" data-post="%s"><a class="ph%s" href="case-%s-v2.html"><img src="%s" alt="%s" loading="lazy" /></a><div>
<span class="kick">%s</span><h2>%s</h2><p>%s</p>%s<div class="thumbs">%s</div><a class="btn md" href="case-%s-v2.html">Read the Whole Blog Post &rarr;</a></div></article>''' % (
        p["slug"], p["cat"], _post_groups[p["slug"]], p["slug"], contain, p["slug"], thumb(p["cardImg"]), e(p.get("cardAlt", "")), e(p["kicker"]), e(p["title"]), e(p["blurb"]), tag_links(p.get("tags", [])), th, p["slug"]))
design_body = '''%s
<section class="section-dark"><div class="wrap">
<div class="design-top">
  <div class="map-box"><span class="label">Design &amp; Signage &middot; Michigan</span><h3>Design Work Across the State</h3><p>Tap a pin to jump to the project.</p><div class="mapwrap"><div class="mapzoom">%s%s</div></div></div>
</div>
<div class="gal-head"><div><span class="label">Gallery</span><h3>Photos &amp; Proofs</h3><p>Tagged by project &mdash; tap any photo to open the full gallery.</p></div><a class="btn md" href="gallery-v2.html">View Full Gallery &rarr;</a></div>
<div class="gal-strip" aria-label="Gallery photos"><div class="gal-track" id="gt">%s</div></div>
<div class="filters" id="f"><button class="fchip on" data-f="all">All Work</button>%s</div>
%s
<div class="more-wrap" id="moreWrap" hidden><button type="button" class="btn md" id="moreBtn">Show More</button></div>
<p style="color:var(--slate);margin-top:10px">More work coming soon.</p>
</div></section>''' % (head("", "Design &amp; Signage", "Identity marks, brand systems, apparel, and print &mdash; plus vehicle graphics and physical signs built around Michigan."), map_svg, pin_html, teaser, _chips, "\n".join(cards))
SHOW_MAP = False   # the "Design Work Across the State" map stays in the page (and keeps its data) but is hidden; set True to show it again
if not SHOW_MAP:
    design_body = design_body.replace('<div class="design-top">', '<div class="design-top" hidden>', 1)
write("design-v2.html", page("Design & Signage", design_body, "Design", """
  /* filter chips + "Show More": the button stays hidden until more than PAGE posts match; then the first PAGE show and each click adds PAGE more */
  (function () {
    var PAGE = 12, shown = PAGE, filter = 'all';
    var posts = [].slice.call(document.querySelectorAll('.post')), wrap = document.getElementById('moreWrap'), btn = document.getElementById('moreBtn');
    function gone(p) { return p.getAttribute('data-gone') === '1'; }
    function render() {
      var n = 0, total = 0;
      posts.forEach(function (p) {
        var match = !gone(p) && (filter === 'all' || (' ' + (p.dataset.tags || '') + ' ').indexOf(' ' + filter + ' ') >= 0);
        p.classList.toggle('f-hide', !match);
        if (match) { total++; n++; }
        p.classList.toggle('pg-hide', match && n > shown);
      });
      var left = total - shown;
      wrap.hidden = left <= 0;
      btn.textContent = 'Show More (' + Math.max(left, 0) + ' Left)';
    }
    document.querySelectorAll('.fchip').forEach(function (b) { b.onclick = function () {
      document.querySelectorAll('.fchip').forEach(function (x) { x.classList.toggle('on', x === b); });
      filter = b.dataset.f; shown = PAGE; render();
    }; });
    btn.onclick = function () { shown += PAGE; render(); };
    document.addEventListener('posts-hidden', render);
    if (location.hash) {   // a link straight to a card further down opens enough of the list to include it
      var t = document.getElementById(location.hash.slice(1)), i = posts.indexOf(t);
      if (i >= 0) shown = Math.max(shown, i + 1);
    }
    window.designPager = { setSize: function (n) { PAGE = n; shown = n; render(); } };
    render();
  })();
  (function () { var t = document.getElementById('gt'); if (!t) return; var set = [].slice.call(t.children);
    set.forEach(function (n) { var c = n.cloneNode(true); c.setAttribute('aria-hidden', 'true'); c.tabIndex = -1; t.appendChild(c); });
    t.style.setProperty('--gal-dur', Math.max(45, set.length * 2.5) + 's'); })();
"""))

# ---------- one page per post ----------
for p in posts:
    body_p = "".join("<p>%s</p>" % e(t) for t in p["body"])
    gal = "".join('<figure><a href="%s" data-lb="%s" data-cap="%s"><img src="%s" alt="%s" loading="lazy" /></a><figcaption>%s</figcaption></figure>' % (img(t["src"]), img(t["src"]), e(t.get("caption", "")), thumb(t["src"]), e(t.get("alt", "")), e(t.get("caption", ""))) for t in p.get("thumbs", []))
    contain = " contain" if p["hero"].endswith(".png") or "lockup" in p["hero"] else ""
    b = '''%s<section class="section-dark"><div class="wrap"><div class="detail">
<div class="hero-img%s"><img src="%s" alt="%s" /></div>%s%s<div class="detail-gal">%s</div>
<p style="margin-top:36px"><a class="btn md" href="design-v2.html">&larr; Back to Design</a></p></div></div></section>''' % (
        head(e(p["kicker"] + (" — " + p["city"] if p.get("city") else "")), e(p["title"])), contain, img(p["hero"]), e(p.get("heroAlt", "")), tag_links(p.get("tags", [])), body_p, gal)
    write("case-%s-v2.html" % p["slug"], page(p["title"], b, "Design"))

# ---------- gallery ----------
tiles = "".join('<a href="%s" data-lb="%s" data-cap="%s" data-tags="%s"><img src="%s" alt="%s" loading="lazy"%s /><span>%s</span></a>' % (
    img(g["src"]), img(g["src"]), e(g.get("caption", "")), " ".join(g.get("tags", [])), thumb(g["src"]), e(g.get("caption", "")),
    (' width="%d" height="%d"' % (g["w"], g["h"])) if g.get("w") else "", e(g.get("caption", ""))) for g in gallery)
counts = {}
for g in gallery:
    for t in g.get("tags", []):
        counts[t] = counts.get(t, 0) + 1
chips = '<button class="fchip on" data-t="">All</button>' + "".join('<button class="fchip" data-t="%s">#%s %d</button>' % (t, t, n) for t, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])))
write("gallery-v2.html", page("Gallery", '%s<section class="section-dark"><div class="wrap"><div class="filters">%s</div><div class="masonry" id="m">%s</div></div></section>' % (
    head("", "Gallery", "Every photo and proof, grouped by tag."), chips, tiles), "Design", """
  function apply(t) {
    document.querySelectorAll('.fchip').forEach(function (b) { b.classList.toggle('on', (b.dataset.t || '') === t); });
    document.querySelectorAll('#m a').forEach(function (a) { var on = !t || (' ' + a.dataset.tags + ' ').indexOf(' ' + t + ' ') >= 0; a.style.display = on ? '' : 'none'; a.toggleAttribute('data-hide', !on); });
  }
  document.querySelectorAll('.fchip').forEach(function (b) { b.onclick = function () { location.hash = b.dataset.t || ''; apply(b.dataset.t || ''); }; });
  apply(location.hash.slice(1));"""))

# ---------- dev ----------
# Steam-store-style project pages: a media viewer on the left (big main video/image + a thumbnail row that includes the video),
# the project text in a panel on the right. Clicking a thumbnail swaps what the viewer shows. Nothing auto-scrolls.
dev = src[src.index('<section class="view" data-view="development">'):]
dev = dev[:dev.index("</section>")]
dev_posts = re.findall(r'<article class="dev-post">(.*?)</article>', dev, re.S)
dev_html = []
for art in dev_posts:
    vid = re.search(r'<video[^>]*poster="([^"]+)"[^>]*data-src="([^"]+)"[^>]*>', art)
    imgs = [(IMG.get(k, k), alt) for k, alt, cap in re.findall(r'<img data-img="([^"]+)" alt="([^"]*)" />\s*<span>(.*?)</span>', art, re.S)]
    svgs = re.findall(r'<svg viewBox="[^"]*".*?</svg>', art, re.S)
    body = re.search(r'<div class="dev-post-body">(.*?)$', art, re.S).group(1)
    label = re.search(r'<span class="label">(.*?)</span>', body).group(1)
    title = re.search(r"<h3>(.*?)</h3>", body).group(1)
    paras = "".join("<p>%s</p>" % p for p in re.findall(r"<p>(.*?)</p>", body, re.S))
    link = re.search(r'<a class="dev-repo-link" href="([^"]+)"[^>]*>(.*?)</a>', body)
    priv = "dev-private-note" in body
    tail = ""
    if link:
        tail += '<a class="btn md" href="%s">%s</a> ' % (link.group(1), link.group(2))
    if priv:
        tail += '<span class="private">Private Repository</span>'

    tiles, main = [], ""
    if vid:
        main = '<video muted loop playsinline preload="none" poster="%s%s" data-src="%s%s" controls></video>' % (REL, vid.group(1), REL, vid.group(2))
        tiles.append('<button type="button" class="dp-tile on" data-type="video" aria-label="Show the video"><img src="%s%s" alt="" /><span class="dp-ic">&#9654;</span></button>' % (REL, vid.group(1)))
    for p, alt in imgs:
        tiles.append('<button type="button" class="dp-tile" data-type="img" data-src="%s%s" data-alt="%s" aria-label="Show this image"><img src="%s%s" alt="" loading="lazy" /></button>' % (REL, p, e(alt), REL, p))
    for sv in svgs:
        tiles.append('<button type="button" class="dp-tile dp-svgtile" data-type="svg" aria-label="Show this diagram"><span class="dp-svgthumb">%s</span><template>%s</template></button>' % (sv, sv))
    if not vid:   # no video: the first still image or diagram is the main view, and it is also the first (selected) thumbnail
        if imgs:
            main = '<img src="%s%s" alt="%s" />' % (REL, imgs[0][0], e(imgs[0][1]))
            tiles[0] = tiles[0].replace('class="dp-tile"', 'class="dp-tile on"', 1)
        elif svgs:
            main = '<div class="dp-svgmain">%s</div>' % svgs[0]
            tiles[0] = tiles[0].replace('class="dp-tile dp-svgtile"', 'class="dp-tile dp-svgtile on"', 1)

    thumbs = ""
    if len(tiles) >= 2:
        thumbs = ('<div class="dp-row"><div class="dp-thumbs">%s</div>'
                  '<div class="dp-ctl"><button type="button" class="dp-arrow" data-dir="-1" aria-label="Scroll thumbnails left">&lsaquo;</button>'
                  '<div class="dp-slider"><div class="dp-knob"></div></div>'
                  '<button type="button" class="dp-arrow" data-dir="1" aria-label="Scroll thumbnails right">&rsaquo;</button></div></div>') % "".join(tiles)
    dev_html.append('<article class="dp"><div class="dp-media"><div class="dp-main">%s</div>%s</div>'
                    '<aside class="dp-info"><div class="dp-text"><span class="kick">%s</span><h2>%s</h2>%s</div><div class="dp-actions">%s</div><button type="button" class="dp-more" hidden aria-expanded="false">Read more</button></aside></article>'
                    % (main, thumbs, label, title, paras, tail))
dev_intro = re.search(r'<div class="page-head">.*?<p>(.*?)</p>', dev, re.S).group(1)
gh = re.search(r'<div class="dev-gh-cta">\s*<a class="btn" href="([^"]+)"[^>]*>(.*?)</a>', dev, re.S)
gh_html = '<div class="gh-cta"><a class="btn md" href="%s" target="_blank" rel="noopener noreferrer">%s</a></div>' % (gh.group(1), gh.group(2)) if gh else ""
write("dev-v2.html", page("Dev", '%s<section class="section-dark"><div class="wrap">%s%s</div></section>' % (
    head("", "Dev", dev_intro).replace("</div></section>", gh_html + "</div></section>", 1), "", chr(10).join(dev_html)), "Dev"))

# ---------- about ----------
ab = src[src.index('<section class="view" data-view="about">'):]
ab = ab[:ab.index("</section>")]
lede = re.search(r'<p class="about-lede">(.*?)</p>', ab, re.S).group(1)
items = re.findall(r'<div class="item">(.*?)</div>\s*(?=<div class="item">|</div>\s*<div class="signoff">)', ab, re.S)
items_html = "".join('<div class="item">%s</div>' % it for it in items)
about_body = '''%s<section class="section-light"><div class="wrap"><p class="lede">%s</p><div class="items">%s</div></div></section>
<section class="cta"><div class="wrap"><div><span class="kick">Open to work</span><h2>What&rsquo;s Next for Your Project?</h2></div><div><p>Hiring for design or sign work? Send a message and I&rsquo;ll get back to you.</p><a class="btn lg light" id="mail" href="#">Email Me</a></div></div></section>''' % (
    head("", "What I Do"), lede, items_html.replace('<span class="label">', '<span class="kick">'))
mail_js = "  document.getElementById('mail') && (document.getElementById('mail').href = 'mailto:' + 'moc.liamg@ssssllew.nimajneb'.split('').reverse().join(''));"
write("about-v2.html", page("About", about_body, "About", mail_js))

# ---------- resume ----------
cards_r = re.findall(r'<div class="resume-card">(.*?)</div>\s*</div>\s*(?=<div class="resume-card">|</div>)', src[src.index('data-view="resumes"'):], re.S)
res_html = []
for c in re.findall(r'<div class="resume-card">(.*?)<div class="resume-actions">(.*?)</div>', src[src.index('data-view="resumes"'):], re.S):
    top, acts = c
    pdf = re.search(r'href="(resumes/[^"]+)"', acts).group(1)
    lab = re.search(r'<span class="label">(.*?)</span>', top).group(1)
    ti = re.search(r"<h3>(.*?)</h3>", top).group(1)
    pa = re.search(r"<p>(.*?)</p>", top, re.S).group(1)
    res_html.append('<div class="rcard"><span class="kick">%s</span><h3>%s</h3><p>%s</p><div class="ract"><a class="btn md" href="%s%s" download>Download PDF &darr;</a><a class="v" href="%s%s" target="_blank" rel="noopener">View Online &#8599;</a></div></div>' % (lab, ti, pa, REL, pdf, REL, pdf))
write("resume-v2.html", page("Resume", '%s<section class="section-light"><div class="wrap"><div class="rcards">%s</div></div></section>' % (
    head("", "Get My Resume", "Grab the resume built for the role you&rsquo;re hiring for."), "".join(res_html)), "Resume"))
print("built", len(posts), "post pages + design, gallery, dev, about, resume")
