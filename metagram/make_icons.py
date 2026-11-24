#!/usr/bin/env python3
"""Render MetaGram app icons from metagram/icons.py and wire them into the app.

Writes, for every icon, Telegram/Resources/art/ayu/<key>/app.svg + app_icon.ico;
for the default icon also the exe/tray icons (icon*.png, icon256.ico, logo_256*).
Then updates the icon lists in ayu_logo.h, icon_picker.cpp and ayu.qrc.

Needs: pip install pillow resvg-py
Run from the repository root after metagram/rebrand.py:
    python metagram/make_icons.py
"""
import io
import pathlib
import re
import shutil
import sys

import resvg_py
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from icons import ICONS, svg  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = ROOT / "Telegram/Resources/art"
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]


def render(svg_text, size):
    data = resvg_py.svg_to_bytes(svg_string=svg_text, width=size, height=size)
    return Image.open(io.BytesIO(bytes(data))).convert("RGBA")


def save_ico(svg_text, path):
    # each size rendered from vectors, not downscaled, so small sizes stay crisp
    frames = [render(svg_text, s) for s in ICO_SIZES]
    frames[-1].save(path, sizes=[(s, s) for s in ICO_SIZES], append_images=frames[:-1])


def read(path):
    return path.read_bytes().decode("utf-8")


def write(path, text):
    path.write_bytes(text.encode("utf-8"))


def nl_of(text):
    return "\r\n" if "\r\n" in text else "\n"


def update_code():
    keys = [i["key"] for i in ICONS]
    const = {k: re.sub(r"\W", "_", k).upper() + "_ICON" for k in keys}

    h = ROOT / "Telegram/SourceFiles/ayu/ui/ayu_logo.h"
    text = read(h)
    nl = nl_of(text)
    block = nl.join(f'ICON({const[k][:-5]}, "{k}");' for k in keys) + nl
    text, n = re.subn(r'(namespace AyuAssets \{\r?\n\r?\n)(ICON\([^\n]*\n)+', lambda m: m.group(1) + block, text)
    assert n == 1, "ayu_logo.h: icon list not found"
    write(h, text)

    cpp = ROOT / "Telegram/SourceFiles/ayu/ui/components/icon_picker.cpp"
    text = read(cpp)
    nl = nl_of(text)
    body = "".join(f"\tAyuAssets::{const[k]},{nl}" for k in keys)
    text, n = re.subn(r'(const QVector<QString> icons\{\r?\n)(.*?)(\};)', lambda m: m.group(1) + body + m.group(3),
                      text, flags=re.S)
    assert n == 1, "icon_picker.cpp: icon list not found"
    write(cpp, text)

    qrc = ROOT / "Telegram/Resources/qrc/ayu/ayu.qrc"
    text = read(qrc)
    nl = nl_of(text)
    text = re.sub(r'[ \t]*<file alias="art/ayu/[^"]+">[^<]+</file>\r?\n', "", text)
    lines = "".join(
        f'        <file alias="art/ayu/{k}/{f}">../../art/ayu/{k}/{f}</file>{nl}'
        for k in keys for f in ("app.svg", "app_icon.ico"))
    text, n = re.subn(r'(<qresource prefix="/gui">\r?\n)', lambda m: m.group(1) + lines, text, count=1)
    assert n == 1, "ayu.qrc: qresource not found"
    write(qrc, text)


def main():
    ayu = ART / "ayu"
    wanted = {i["key"] for i in ICONS}
    for d in ayu.iterdir():
        if d.is_dir() and d.name not in wanted:
            shutil.rmtree(d)

    for icon in ICONS:
        d = ayu / icon["key"]
        d.mkdir(exist_ok=True)
        (d / "app.svg").write_text(svg(icon, rounded=False), encoding="utf-8", newline="\n")
        save_ico(svg(icon, rounded=True), d / "app_icon.ico")

    default = svg(ICONS[0], rounded=True)
    for base in (16, 32, 48, 64, 128, 256, 512):
        render(default, base).save(ART / f"icon{base}.png")
        render(default, base * 2).save(ART / f"icon{base}@2x.png")
    render(default, 1024).save(ART / "icon_round512@2x.png")
    render(default, 256).save(ART / "logo_256_no_margin.png")
    logo = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    logo.paste(render(default, 224), (16, 16))
    logo.save(ART / "logo_256.png")
    save_ico(default, ART / "icon256.ico")
    (ROOT / "metagram/icon.svg").write_text(default, encoding="utf-8", newline="\n")
    render(default, 512).save(ROOT / "metagram/icon_preview.png")

    update_code()
    print(f"{len(ICONS)} icons written")


if __name__ == "__main__":
    main()
