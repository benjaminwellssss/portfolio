"""Make the clean web addresses work on GitHub Pages.

    python tools/build_routes.py

GitHub Pages only serves files that exist, so every top-level page (/design, /about, /resumes, /development,
/gallery) gets its own folder holding a copy of index.html, and 404.html is a copy too: it catches the dynamic
addresses (/case/<post>, /gallery/<tag>), including posts added later in /admin/. The page works out its own
address in a tiny script at the top, so the copies are identical. Run this after every edit to index.html
(tools/check_site.py fails if a copy is out of date).
"""
import os
import shutil

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTES = ["design", "about", "resumes", "development", "gallery"]


def targets():
    return [os.path.join(SITE, r, "index.html") for r in ROUTES] + [os.path.join(SITE, "404.html")]


if __name__ == "__main__":
    src = os.path.join(SITE, "index.html")
    for t in targets():
        os.makedirs(os.path.dirname(t), exist_ok=True)
        shutil.copyfile(src, t)
    print("copied index.html to", len(targets()), "route files")
