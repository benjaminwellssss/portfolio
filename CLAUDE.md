# Benjamin Wells Portfolio Site

This folder is a git clone of Ben's live portfolio site repo.

## Repo / hosting
- Remote: `https://github.com/benjaminwellssss/portfolio.git` (branch `main`)
- Hosted via GitHub Pages, custom domain `bwells.online` (CNAME file in this repo), fallback URL `https://benjaminwellssss.github.io/portfolio/`
- Auth: this machine has a cached credential via Windows Git Credential Manager (`credential.helper=manager` at the system git config level). `git push` from here should work without a login prompt. If GCM ever needs re-auth, it opens a browser window for the user to sign into GitHub — that's normal, just wait for them to complete it.

## IMPORTANT — push discipline
**Only run `git commit` / `git push` when the user explicitly asks for it in that turn.** Making edits and staging them is fine; do not push proactively just because a task is "done." If the user says something like "commit when complete with these tasks," that counts as explicit — otherwise wait to be told.

## Site architecture
The entire site is **one self-contained `index.html`** file (no build step, no other JS/CSS files):
- All images are embedded as base64 `data:` URIs inside a JS `IMG` map (`var IMG = {...}`), keyed by a short filename. HTML uses `<img data-img="key.jpg">` and a script on load resolves `data-img` → real `src` from `IMG`.
- It's a client-side SPA: `<section class="view" data-view="...">` blocks are shown/hidden based on `location.hash`, handled by a `show()` function. Valid view names are listed in `var valid = [...]`.
- Case studies (both Design and Sign Design pages) live in one `var CASE_STUDIES = {...}` object, keyed by slug, rendered into the shared `data-view="case"` template via `renderCase(slug)`. **Static list-page cards for each case study are separately hand-written in HTML** (not generated from `CASE_STUDIES`) — so when adding/editing a case study, update both: the `CASE_STUDIES` JS entry (for the detail page) and the matching `<article class="case-card">` block in the relevant page's `.case-grid` (for the list view).
- The Sign Design page has a hand-drawn simplified Michigan Lower Peninsula SVG outline with clickable `.mi-pin` dots; clicking a pin scrolls down to the matching case-card via `id="post-<slug>"` on the article (see the click handler near `bioText` setup in the script).
- Body/thumbnail-caption text set via `.textContent` in JS does **not** decode HTML entities — use real Unicode characters or `’`/`—` JS escapes there, not `&rsquo;`/`&mdash;`. Static HTML (kickers via `.innerHTML`, `case-blurb` paragraphs written directly in markup) can use HTML entities normally.
- The email link (`#emailLink`) is deliberately not present as plain text in the source — it's assembled from a reversed string at runtime to deter scraping. Don't "simplify" it back to a plain `mailto:` string in markup.

## Workflow for site changes
1. Edit `index.html` directly (or via a scratch Python script for large/repetitive edits — surgical string replacements with `assert count == 1` guards are the pattern used so far, to avoid corrupting the file).
2. Sanity-check before considering a change done:
   - `node` a quick script that extracts the `<script>` contents and runs `new Function(...)` on it to confirm it still parses.
   - Cross-check that every `data-img="..."` / `src: '...'` / `hero: '...'` reference has a matching key in `IMG`.
3. Preview locally before pushing: a `.claude/launch.json` config named `static-preview` (python `http.server`) pointed at this folder works with the `preview_start` tool for a real render check.
4. Only after the user confirms (or explicitly asks to ship): `git add index.html`, `git commit -m "..."`, `git push origin main`.

## Known context
- No real domain/email hosting set up yet beyond the GitHub Pages + Hover DNS combo already described above.
- Ben's day-to-day requests come in fast and often bundle several unrelated changes in one message — read carefully, they're usually all distinct asks, not one compound request.
