"""Sanity-check the site: JS parses, every image/resume path exists, every reference resolves.

    python tools/check_site.py [site_dir]
"""
import os, re, subprocess, sys

D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(D, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()
problems = []

# 1. every inline script parses
scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
tmp = os.path.join(os.environ["TEMP"], "_chk_script.js")
ok_all = True
for i, code in enumerate(scripts):
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(code)
    r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    if r.returncode != 0:
        ok_all = False
        problems.append("JS PARSE ERROR in script %d: %s" % (i, r.stderr.strip()[:300]))
print("scripts parse:", ok_all, "| scripts:", len(scripts), "| chars:", sum(len(c) for c in scripts))

# 2. IMG map + IMG_DIM
a = html.index("  var IMG = {")
b = html.index("\n  };", a)
img = dict(re.findall(r"^    '([^']+)': '([^']+)',?$", html[a:b], re.M))
c = html.index("  var IMG_DIM = {")
d = html.index("\n  };", c)
dim = dict(re.findall(r"^    '([^']+)': \[(\d+), (\d+)\]", html[c:d], re.M) and
           [(k, (w, h)) for k, w, h in re.findall(r"^    '([^']+)': \[(\d+), (\d+)\]", html[c:d], re.M)])
e = html.index("  var IMG_T = {")
f2 = html.index("\n  };", e)
thumbs_map = dict(re.findall(r"^    '([^']+)': '([^']+)',?$", html[e:f2], re.M))
miss_t = [p for p in thumbs_map.values() if not os.path.exists(os.path.join(D, p))]
print("IMG_T thumbs:", len(thumbs_map), "| missing on disk:", miss_t or "none")
if miss_t or not set(thumbs_map) <= set(img):
    problems.append("IMG_T problem")
print("IMG keys:", len(img), "| IMG_DIM keys:", len(dim))
if set(img) != set(dim):
    problems.append("IMG and IMG_DIM keys differ: " + str(set(img) ^ set(dim)))
missing_files = [p for p in img.values() if not os.path.exists(os.path.join(D, p))]
if missing_files:
    problems.append("IMG paths missing on disk: " + str(missing_files))

# 3. references resolve
content_refs = set()
for _f in ("posts", "gallery"):
    _p = os.path.join(D, "content", _f + ".json")
    if os.path.exists(_p):
        content_refs |= set(re.findall(r'"(?:src|hero|cardImg)":\s*"([^"]+)"', open(_p, encoding="utf-8").read()))
miss_c = [x for x in content_refs if not os.path.exists(os.path.join(D, x))]
miss_c += [x for x in content_refs if x.startswith("img/") and not os.path.exists(os.path.join(D, "img", "t", os.path.splitext(os.path.basename(x))[0] + ".webp"))]
print("content image refs:", len(content_refs), "| missing file or thumbnail:", miss_c or "none")
if miss_c:
    problems.append("content refs missing: " + str(miss_c))
data_img = set(re.findall(r'data-img="([^"]+)"', html))
thumbs = set(re.findall(r"src:\s*'([^']+\.(?:jpg|png|gif|webp))'", html))
heroes = set(re.findall(r"hero:\s*'([^']+\.(?:jpg|png|gif|webp))'", html))
for label, refs in (("data-img", data_img), ("thumb src", thumbs), ("hero", heroes)):
    miss = refs - set(img)
    print(f"{label} refs: {len(refs)} | missing from IMG: {sorted(miss) or 'none'}")
    if miss:
        problems.append(f"{label} refs missing: {sorted(miss)}")
unused = set(img) - data_img - thumbs - heroes - {k for k, v in img.items() if v in content_refs}
print("IMG keys never referenced:", sorted(unused) or "none")

# 4. every static path in the html exists
paths = set(re.findall(r"""(?:href|src|content|data|data-src|poster)=['"]((?:img|resumes|video)/[^'"]+)['"]""", html))
paths |= set(re.findall(r"""'((?:img|resumes)/[^']+)'""", html))
miss = [p for p in paths if not os.path.exists(os.path.join(D, p))]
print("static path refs:", len(paths), "| missing on disk:", miss or "none")
if miss:
    problems.append("missing static paths: " + str(miss))

# 5. no embedded data URIs left; sizes
print("embedded data: URIs:", html.count("data:image") + html.count("data:application"))
tot = sum(os.path.getsize(os.path.join(D, "img", f)) for f in os.listdir(os.path.join(D, "img")))
print("index.html KB:", os.path.getsize(os.path.join(D, "index.html")) // 1024, "| img/ KB:", tot // 1024)
files_on_disk = set("img/" + f for f in os.listdir(os.path.join(D, "img")))
orphans = files_on_disk - set(img.values()) - paths
print("orphan files in img/:", sorted(orphans) or "none")

# route copies (clean addresses) must match index.html
sys.path.insert(0, os.path.join(D, "tools"))
import build_routes
stale = [os.path.relpath(t, D) for t in build_routes.targets() if not os.path.exists(t) or open(t, encoding="utf-8").read() != html]
print("route copies out of date:", stale or "none")
if stale:
    problems.append("run python tools/build_routes.py: " + str(stale))

print("RESULT:", "OK" if not problems else "PROBLEMS")
for p in problems:
    print(" -", p)
sys.exit(1 if problems else 0)
