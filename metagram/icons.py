"""MetaGram app icons. The first one is the default icon.

Each icon is a 512x512 SVG: a background (solid color or two-color gradient)
and a glyph. In `glyph`, FG is the glyph color, BG the background color.
Edit this list and run `python metagram/make_icons.py`.
"""

ROUND = 'fill="none" stroke="FG" stroke-linecap="round" stroke-linejoin="round"'

CROSSED = (f'<circle cx="256" cy="256" r="118" {ROUND} stroke-width="38"/>'
           f'<path d="M174 338L338 174" {ROUND} stroke-width="38"/>')
PEAKS = f'<path d="M120 352L200 164L256 296L312 164L392 352" {ROUND} stroke-width="44"/>'
GHOST = ('<path d="M256 124C192 124 156 172 156 230V378L190 352L223 380L256 352L289 380'
         'L322 352L356 378V230C356 172 320 124 256 124Z" fill="FG"/>'
         '<circle cx="218" cy="236" r="18" fill="EYE"/><circle cx="294" cy="236" r="18" fill="EYE"/>')
MOON = '<path d="M296 128A140 140 0 1 0 392 336A112 112 0 1 1 296 128Z" fill="FG"/>'
EYE_CLOSED = (f'<path d="M140 232Q256 340 372 232" {ROUND} stroke-width="36"/>'
              f'<path d="M180 286L162 326M256 306V350M332 286L350 326" {ROUND} stroke-width="30"/>')
EYE = ('<path d="M112 256Q256 120 400 256Q256 392 112 256Z" fill="FG"/>'
       '<circle cx="256" cy="256" r="54" fill="BG"/>')
SPARK = ('<path d="M256 112C266 204 308 246 400 256C308 266 266 308 256 400C246 308 204 266 '
         '112 256C204 246 246 204 256 112Z" fill="FG"/>')
PLANET = ('<circle cx="256" cy="256" r="84" fill="FG"/>'
          f'<ellipse cx="256" cy="256" rx="170" ry="54" transform="rotate(-24 256 256)" {ROUND} stroke-width="26"/>'
          '<path d="M178 216A84 84 0 0 1 334 216" fill="FG"/>')
BUBBLE = ('<path d="M256 134C176 134 126 186 126 248C126 284 142 314 168 334L158 384L216 358'
          f'Q236 362 256 362C336 362 386 310 386 248C386 186 336 134 256 134Z" {ROUND} stroke-width="36"/>')
SHADOW = ('<circle cx="214" cy="256" r="96" fill="FG"/>'
          f'<circle cx="310" cy="256" r="96" {ROUND} stroke-width="28"/>')
MASK = ('<path d="M112 222Q112 190 150 190H362Q400 190 400 222V258Q400 316 340 316Q296 316 256 282'
        'Q216 316 172 316Q112 316 112 258Z" fill="FG"/>'
        '<ellipse cx="190" cy="248" rx="38" ry="24" fill="BG"/><ellipse cx="322" cy="248" rx="38" ry="24" fill="BG"/>')
RING = (f'<path d="M352 176A130 130 0 1 0 380 256" {ROUND} stroke-width="44"/>'
        '<circle cx="380" cy="176" r="26" fill="FG"/>')

# key: folder name under Telegram/Resources/art/ayu/ and the saved setting value
ICONS = [
    dict(key="default", bg="#111111", glyph=CROSSED),
    dict(key="light", bg="#FFFFFF", fg="#111111", glyph=CROSSED),
    dict(key="neon", bg="#0A0F2C", fg=("#22D3EE", "#E879F9"), glyph=CROSSED),
    dict(key="gold", bg="#111111", fg=("#FDE68A", "#D97706"), glyph=CROSSED),
    dict(key="pink", bg="#FF2D78", glyph=CROSSED),
    dict(key="ocean", bg=("#0EA5E9", "#4F46E5"), glyph=CROSSED),
    dict(key="peaks", bg="#111111", glyph=PEAKS),
    dict(key="ghost", bg="#6D4AFF", glyph=GHOST),
    dict(key="ghostnight", bg="#0B1026", glyph=GHOST, eye="#22D3EE"),
    dict(key="moon", bg="#2340D9", glyph=MOON),
    dict(key="aurora", bg=("#10B981", "#7C3AED"), glyph=MOON),
    dict(key="sleepy", bg="#111111", glyph=EYE_CLOSED),
    dict(key="eye", bg="#7C3AED", glyph=EYE),
    dict(key="spark", bg="#FF5A36", glyph=SPARK),
    dict(key="sunset", bg=("#F97316", "#DB2777"), glyph=SPARK),
    dict(key="planet", bg="#0EA5E9", glyph=PLANET),
    dict(key="bubble", bg="#10B981", glyph=BUBBLE),
    dict(key="shadow", bg="#111111", glyph=SHADOW),
    dict(key="mask", bg="#B91C1C", glyph=MASK),
    dict(key="ring", bg="#E11D48", glyph=RING),
]


def _paint(spec, gid):
    """Return (defs, paint) for a color or a (from, to) gradient."""
    if isinstance(spec, tuple):
        a, b = spec
        return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
                f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>',
                f"url(#{gid})")
    return "", spec


def svg(icon, rounded):
    """SVG text. rounded=True gives a squircle (Windows icon), else a full square
    (the app clips its in-app logo to a circle itself)."""
    bg_defs, bg = _paint(icon["bg"], "bg")
    fg_defs, fg = _paint(icon.get("fg", "#FFFFFF"), "fg")
    solid_bg = icon["bg"] if isinstance(icon["bg"], str) else icon["bg"][1]
    glyph = (icon["glyph"]
             .replace("EYE", icon.get("eye", "BG"))
             .replace("FG", fg)
             .replace("BG", solid_bg))
    rx = ' rx="116"' if rounded else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">'
            f"<defs>{bg_defs}{fg_defs}</defs>"
            f'<rect width="512" height="512"{rx} fill="{bg}"/>{glyph}</svg>\n')
