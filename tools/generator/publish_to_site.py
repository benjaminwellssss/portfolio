"""Copies the offline demo into the real site repo as unlisted test pages.

    python build_demo.py          # regenerate the demo from the site content first
    python publish_to_site.py     # then publish it

Test pages (not linked from the live pages, marked noindex):
    /home2/  /design2/  /gallery2/  /about2/  /resume2/  /dev2/  /case2/<post>/
Shared files go in /assets2/. When the test pages are approved, they replace the originals.
"""
import os
import re
import shutil
import sys

# --live publishes to the real addresses (/, /design/, /case/<post>/, /assets/); without it, the unlisted *2 test pages
LIVE = "--live" in sys.argv
SUF = "" if LIVE else "2"

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("PORTFOLIO_DIR") or os.path.normpath(os.path.join(HERE, "..", ".."))   # the site (repo root)

import hashlib


def _ver(name):
    return hashlib.md5(open(os.path.join(HERE, name), "rb").read().replace(b"\r\n", b"\n")).hexdigest()[:8]   # same stamp on Windows and Linux


# cache-busting: the version changes whenever the file changes, so browsers never keep an old stylesheet
VER_CSS, VER_JS = _ver("v2.css"), _ver("v2.js")

if LIVE:
    PAGES = {"index-v2.html": "", "design-v2.html": "design", "gallery-v2.html": "gallery",
             "about-v2.html": "about", "resume-v2.html": "resumes", "dev-v2.html": "development"}
    CASE, ASSETS = "case", "assets"
else:
    PAGES = {"index-v2.html": "home2", "design-v2.html": "design2", "gallery-v2.html": "gallery2",
             "about-v2.html": "about2", "resume-v2.html": "resume2", "dev-v2.html": "dev2"}
    CASE, ASSETS = "case2", "assets2"


import json
HIDDEN = [x["slug"] for x in json.load(open(os.path.join(SITE, "content", "posts.json"), encoding="utf-8"))["posts"] if x.get("hidden")]


_DIMS = {}


def _dims(path):
    """width and height of a site image, so every <img> can carry them and the page does not jump while images load"""
    if path not in _DIMS:
        try:
            from PIL import Image
            with Image.open(os.path.join(SITE, path.lstrip("/"))) as im:
                _DIMS[path] = im.size
        except Exception:
            _DIMS[path] = None
    return _DIMS[path]


def add_sizes(html):
    def one(m):
        tag = m.group(0)
        if " width=" in tag or " height=" in tag:
            return tag
        src = re.search(r'src="(/img/[^"?#]+)"', tag)
        d = _dims(src.group(1)) if src else None
        return tag.replace("<img ", '<img width="%d" height="%d" ' % d, 1) if d else tag
    return re.sub(r"<img [^>]*>", one, html)


def medium_cards(html):
    """home-page cards show a photo at about 330px wide: serve an 800px copy (img/m/) instead of the full 1600px one"""
    def one(m):
        name = m.group(2)
        src = os.path.join(SITE, "img", name)
        dst = os.path.join(SITE, "img", "m", name)
        if not os.path.exists(dst) and os.path.exists(src):
            try:
                from PIL import Image
                with Image.open(src) as im:
                    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                    im.thumbnail((800, 800))
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    im.save(dst, "WEBP", quality=80, method=6)
            except Exception:
                return m.group(0)
        return m.group(1) + "/img/m/" + name + '"' if os.path.exists(dst) else m.group(0)
    return re.sub(r'(<div class="shot[^"]*"><img src=")/img/([^"/]+\.webp)"', one, html)


def minify_css(css):
    """safe, simple: drop comments and collapse whitespace (calc() operators keep their spaces)"""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css)
    css = re.sub(r"\s*([,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    return css.strip()


def fix(html):
    # client-logo lines tagged "// post:<slug>" go away while that post is hidden
    for slug in HIDDEN:
        html = re.sub(r"[^\n]*// post:%s[^\n]*\n" % re.escape(slug), "", html)
    # case pages first (their file names contain "-v2.html" too)
    html = re.sub(r'href="case-([a-z0-9-]+)-v2\.html"', lambda m: 'href="/%s/%s/"' % (CASE, m.group(1)), html)
    for src, folder in PAGES.items():
        html = html.replace('href="%s#' % src, 'href="/%s/#' % folder if folder else 'href="/#').replace('href="%s"' % src, 'href="/%s/"' % folder if folder else 'href="/"')
    html = html.replace('href="v2.css"', 'href="/%s/v2.css?v=%s"' % (ASSETS, VER_CSS)).replace('src="v2.js"', 'src="/%s/v2.js?v=%s"' % (ASSETS, VER_JS))
    html = html.replace("../ben-wells-design/", "/")
    if LIVE:
        t = re.search(r"<title>(.*?)</title>", html).group(1)
        og = ('<meta property="og:title" content="%s" /><meta property="og:description" content="Graphic design portfolio &mdash; logos, brand systems, apparel graphics, and print work." />'
              '<meta property="og:image" content="https://www.bwells.online/img/logo.png" /><meta property="og:type" content="website" /><meta name="twitter:card" content="summary" />') % t
        hashfix = ("<script>(function(){var h=location.hash.replace(/^#\/?/,'');if(location.pathname==='/'&&/^(design|gallery|about|case|resumes|development|signs)(\/|$)/.test(h))"
                   "location.replace('/'+(h==='signs'?'design/':h.replace(/\/?$/,'/')));})();</script>")
        return add_sizes(medium_cards(html.replace("</head>", og + hashfix + "</head>", 1)))
    # unlisted test pages
    html = html.replace("<head>", '<head><meta name="robots" content="noindex, nofollow">', 1) if "<head>" in html else html.replace('<meta charset="utf-8" />', '<meta charset="utf-8" /><meta name="robots" content="noindex, nofollow" />', 1)
    # the generated CSS has image urls too
    return add_sizes(html)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)


count = 0
for name in sorted(os.listdir(HERE)):
    if not name.endswith("-v2.html"):
        continue
    html = fix(open(os.path.join(HERE, name), encoding="utf-8").read())
    if name in PAGES:
        out = os.path.join(SITE, PAGES[name], "index.html")
    elif name.startswith("case-"):
        slug = name[len("case-"):-len("-v2.html")]
        out = os.path.join(SITE, CASE, slug, "index.html")
    else:
        continue
    write(out, html)
    count += 1

# posts that are no longer generated (hidden or deleted) must not stay on the site
keep = {n[len("case-"):-len("-v2.html")] for n in os.listdir(HERE) if n.startswith("case-") and n.endswith("-v2.html")}
case_dir = os.path.join(SITE, CASE)
if os.path.isdir(case_dir):
    for slug in os.listdir(case_dir):
        if slug not in keep:
            shutil.rmtree(os.path.join(case_dir, slug))
            print("removed page for", slug)

css = open(os.path.join(HERE, "v2.css"), encoding="utf-8").read().replace("../ben-wells-design/", "/")
write(os.path.join(SITE, ASSETS, "v2.css"), minify_css(css) if LIVE else css)
shutil.copyfile(os.path.join(HERE, "v2.js"), os.path.join(SITE, ASSETS, "v2.js"))
print("published", count, "pages + assets2/ into", SITE, "(live)" if LIVE else "(test)")
