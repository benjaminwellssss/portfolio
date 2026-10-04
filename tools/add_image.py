"""Add or replace an image on the site.

    python tools/add_image.py KEY SOURCE_FILE [--no-thumb]

KEY is the name the page code uses (e.g. legion_van_9999.jpg). The source is converted to WebP
(longest side capped at 1600px) into img/, a 480px thumbnail goes into img/t/, and the IMG, IMG_T and
IMG_DIM maps in index.html are updated. Animated GIFs and tiny PNGs are copied as-is.
Needs ffmpeg and ffprobe on PATH.
"""
import os
import re
import shutil
import subprocess
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAP = "scale='if(gt(iw,ih),min({n},iw),-2)':'if(gt(iw,ih),-2,min({n},ih))'"


def run(args):
    subprocess.run(args, check=True, capture_output=True)


def dims(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path]
    ).decode().strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


def upsert(html, var, key, value):
    """Set `    'key': value,` inside `var NAME = { ... };`, replacing an existing line or appending."""
    a = html.index(f"  var {var} = {{")
    b = html.index("\n  };", a)
    block = html[a:b]
    line = f"    '{key}': {value},"
    pat = re.compile(r"^    '" + re.escape(key) + r"': .*$", re.M)
    block = pat.sub(line, block) if pat.search(block) else block + "\n" + line
    return html[:a] + block + html[b:]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    key, src = args
    want_thumb = "--no-thumb" not in sys.argv
    ext = os.path.splitext(src)[1].lower().lstrip(".")
    stem = os.path.splitext(key)[0]
    os.makedirs(os.path.join(SITE, "img", "t"), exist_ok=True)

    thumb = None
    if ext == "gif" or (ext == "png" and os.path.getsize(src) < 40 * 1024):
        out_name = f"{stem}.{ext}"
        shutil.copy(src, os.path.join(SITE, "img", out_name))
    else:
        out_name = f"{stem}.webp"
        out = os.path.join(SITE, "img", out_name)
        if ext in ("jpg", "jpeg"):
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", CAP.format(n=1600), "-c:v", "libwebp", "-quality", "72", "-compression_level", "6", out])
        else:
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", CAP.format(n=1600), "-c:v", "libwebp", "-lossless", "1", "-compression_level", "6", out])
            if os.path.getsize(out) > os.path.getsize(src):
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", CAP.format(n=1600), "-c:v", "libwebp", "-quality", "90", "-compression_level", "6", out])
        if want_thumb:
            t_out = os.path.join(SITE, "img", "t", out_name)
            if ext in ("jpg", "jpeg"):
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", CAP.format(n=480), "-c:v", "libwebp", "-quality", "70", "-compression_level", "6", t_out])
            else:
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", CAP.format(n=480), "-c:v", "libwebp", "-lossless", "1", "-compression_level", "6", t_out])
            thumb = f"img/t/{out_name}"

    w, h = dims(os.path.join(SITE, "img", out_name))
    index = os.path.join(SITE, "index.html")
    with open(index, "r", encoding="utf-8") as f:
        html = f.read()
    html = upsert(html, "IMG", key, f"'img/{out_name}'")
    html = upsert(html, "IMG_DIM", key, f"[{w}, {h}]")
    if thumb:
        html = upsert(html, "IMG_T", key, f"'{thumb}'")
    with open(index, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{key} -> img/{out_name} ({w}x{h}){' + ' + thumb if thumb else ''}")


if __name__ == "__main__":
    main()
