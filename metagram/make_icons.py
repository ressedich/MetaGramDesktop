#!/usr/bin/env python3
"""Draw the MetaGram app icon and write every icon file the app uses.

Needs Pillow (pip install pillow). Run from the repository root:
    python metagram/make_icons.py
The vector version is metagram/icon.svg (also copied to the app resources).
"""
import pathlib
import shutil

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = ROOT / "Telegram/Resources/art"
SVG = ROOT / "metagram/icon.svg"

TOP_LEFT = (0x7B, 0x5C, 0xFF)      # violet
BOTTOM_RIGHT = (0x1F, 0xB6, 0xFF)  # sky blue
# "M" stroke in a 512x512 box; keep in sync with icon.svg
M_POINTS = [(150, 350), (150, 170), (256, 290), (362, 170), (362, 350)]
M_WIDTH = 56
SS = 4  # supersampling factor


def draw(size, margin=0):
    big = size * SS
    inner = big - 2 * margin * SS
    # diagonal gradient
    n = 256  # a smooth gradient survives upscaling
    grad = Image.new("RGB", (n, n))
    px = grad.load()
    for y in range(n):
        for x in range(n):
            t = (x + y) / (2 * (n - 1))
            px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(TOP_LEFT, BOTTOM_RIGHT))
    grad = grad.resize((inner, inner), Image.BICUBIC)
    mask = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, inner - 1, inner - 1), fill=255)
    circle = Image.new("RGBA", (inner, inner), (0, 0, 0, 0))
    circle.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(circle)
    k = inner / 512
    pts = [(x * k, y * k) for x, y in M_POINTS]
    w = round(M_WIDTH * k)
    d.line(pts, fill="white", width=w, joint="curve")
    r = w / 2
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill="white")

    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    out.paste(circle, (margin * SS, margin * SS), circle)
    return out.resize((size, size), Image.LANCZOS)


def main():
    master = draw(1024)
    cache = {}

    def at(size, margin=0):
        key = (size, margin)
        if key not in cache:
            cache[key] = draw(size, margin) if size <= 256 or margin else master.resize((size, size), Image.LANCZOS)
        return cache[key]

    for base in (16, 32, 48, 64, 128, 256, 512):
        at(base).save(ART / f"icon{base}.png")
        at(base * 2).save(ART / f"icon{base}@2x.png")
    at(1024).save(ART / "icon_round512@2x.png")
    at(256).save(ART / "logo_256_no_margin.png")
    at(256, margin=16).save(ART / "logo_256.png")

    ico_sizes = [(s, s) for s in (16, 24, 32, 48, 64, 128, 256)]
    master.save(ART / "icon256.ico", sizes=ico_sizes)

    default = ART / "ayu/default"
    master.save(default / "app_icon.ico", sizes=ico_sizes)
    shutil.copyfile(SVG, default / "app.svg")
    master.resize((512, 512), Image.LANCZOS).save(ROOT / "metagram/icon_preview.png")
    print("icons written")


if __name__ == "__main__":
    main()
