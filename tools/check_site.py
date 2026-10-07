"""Sanity-check the generated site: every page's local links, images, scripts and styles resolve to real files.

    python tools/check_site.py [site_dir]

Checks the home page, the section folders, /case/<post>/ and 404.html. Exits 1 if anything is missing.
"""
import os, re, sys
from urllib.parse import unquote

D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"admin", "worker", "tools", "docs", "content", "img", "video", "resumes_pdf", ".git"}
pages = [os.path.join(D, "index.html"), os.path.join(D, "404.html")]
for sec in ("design", "gallery", "about", "resumes", "development"):
    pages.append(os.path.join(D, sec, "index.html"))
case = os.path.join(D, "case")
if os.path.isdir(case):
    pages += [os.path.join(case, s, "index.html") for s in sorted(os.listdir(case))]
problems, refs_total = [], 0


def resolve(url):
    path = unquote(url.split("#")[0].split("?")[0])
    full = os.path.join(D, path.lstrip("/"))
    return os.path.isfile(full) or os.path.isfile(os.path.join(full, "index.html"))


for p in pages:
    if not os.path.exists(p):
        problems.append("missing page: " + os.path.relpath(p, D)); continue
    html = open(p, encoding="utf-8").read()
    refs = set(re.findall(r'''(?:href|src|data-src|poster)=["'](/[^"'#][^"']*)["']''', html))
    refs |= set(re.findall(r'''url\(["']?(/[^"')]+)''', html))
    for r in refs:
        refs_total += 1
        if not resolve(r):
            problems.append("%s -> %s" % (os.path.relpath(p, D), r))
    if "noindex" in html and p != os.path.join(D, "404.html"):
        problems.append("noindex on a real page: " + os.path.relpath(p, D))
css = os.path.join(D, "assets", "v2.css")
if os.path.exists(css):
    for r in set(re.findall(r'''url\(["']?(/[^"')]+)''', open(css, encoding="utf-8").read())):
        refs_total += 1
        if not resolve(r):
            problems.append("assets/v2.css -> " + r)
else:
    problems.append("missing assets/v2.css")
print("pages checked:", len(pages), "| references checked:", refs_total)
print("PROBLEMS:" if problems else "all good", *problems, sep="\n  ")
sys.exit(1 if problems else 0)
