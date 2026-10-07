# Admin API

A small Cloudflare Worker that powers the hidden `/admin/` page. It checks the admin password, then commits
`content/posts.json`, `content/gallery.json` and uploaded images to this repository, and GitHub Pages rebuilds the
site from that commit (about a minute).

Nothing secret lives in the repo. Three secrets are stored in the Worker:

| Secret | What it is |
|---|---|
| `ADMIN_PASSWORD` | The password typed into `/admin/` |
| `SESSION_SECRET` | Any long random string; signs login tokens |
| `GITHUB_TOKEN` | A fine-grained GitHub token for this repository only, permission **Contents: read and write** |

## One-time setup

1. Create a free Cloudflare account.
2. Create the GitHub token: GitHub > Settings > Developer settings > Fine-grained tokens > Generate. Repository access:
   only this repository. Permissions: Contents, read and write.
3. From the `worker/` folder:

   ```bash
   npx wrangler login
   npx wrangler secret put ADMIN_PASSWORD
   npx wrangler secret put SESSION_SECRET
   npx wrangler secret put GITHUB_TOKEN
   npx wrangler deploy
   ```

4. Copy the `https://portfolio-admin.<account>.workers.dev` address that `deploy` prints into `admin/config.js`
   (`window.ADMIN_API = '...'`), commit and push. Then open `/admin/` on the live site.

## Changing the password

```bash
npx wrangler secret put ADMIN_PASSWORD
```

It takes effect immediately. Signing in lasts 12 hours per browser tab.

## Notes

- Only the origins listed in `wrangler.toml` (`ALLOWED_ORIGINS`) can call the API.
- Five wrong passwords in a row lock that address out for ten minutes (best effort; use a long password).
- The admin only edits the two JSON files and adds images. Removing a photo from the gallery leaves its file in `img/`.
- Local testing: put the three secrets in `worker/.dev.vars` (ignored by git) and run `npx wrangler dev --local`.
