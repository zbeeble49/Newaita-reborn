#!/usr/bin/env python3
"""Generate the Newaita-reborn color variants.

Every variant is built from the two hand-made base themes:

    Newaita-reborn        (light)
    Newaita-reborn-dark   (dark)

A variant symlinks everything except `places/` to its base theme and gets its
own copy of `places/` in which the blue folder palette is replaced.

* Color variants: the palette comes from the folder-<color>.svg templates in
  Newaita-reborn/places/48 (back tab and front color); the emblem tint comes from
  the EMBLEM table below.
* Chameleon variants: the folder colors are replaced by KDE's
  `ColorScheme-Highlight` (fill:currentColor). KIconLoader feeds in the active
  Plasma accent/selection color at runtime, so the folders follow the
  Plasma color settings. Shading is done with black/white overlays.

Usage:  tools/build-variants.py [--clean]
  --clean   remove all generated Newaita-reborn-* variants first
"""
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASES = {"": "Newaita-reborn", "-dark": "Newaita-reborn-dark"}
SHARED_DIRS = ["actions", "apps", "devices", "emblems", "mimetypes", "panel"]
SHARED_LINKS = {"categories": "apps/", "status": "panel/"}

# Blue palette used by the base themes (as written in the SVGs).
BLUE_BACK = "rgb(12.941177%,58.823532%,95.294118%)"    # #2196F3  back tab
BLUE_FRONT = "rgb(25.882354%,64.705884%,96.078432%)"   # #42A5F5  folder body
BLUE_EMBLEM = "rgb(56.470591%,79.215688%,97.647059%)"  # #90CAF9  emblem/symbol

# Emblem tint per color (Material 200-ish of the template hue). Back/front
# colors are read from the templates themselves.
EMBLEM = {
    "black": "#BDBDBD",
    "brown": "#BCAAA4",
    "gray": "#E0E0E0",
    "green": "#A5D6A7",
    "lime": "#E6EE9C",
    "orange": "#FFAB91",
    "pink": "#F48FB1",
    "purple": "#CE93D8",
    "red": "#EF9A9A",
    "teal": "#80CBC4",
    "yellow": "#FFECB3",
}
# Extra per-color substitutions (taken over from the original gray variant:
# keeps the tar emblem readable on light gray).
EXTRA = {
    "gray": {"rgb(90.196079%,90.196079%,90.196079%)": "#FEFEFE"},
}
TEMPLATE_DIR = os.path.join(ROOT, "Newaita-reborn", "places", "48")
# Template icons must never be recolored.
TEMPLATE_RE = re.compile(r"^folder-(%s|blue|grey|root)\.svg$" % "|".join(EMBLEM))

# Chameleon shading (on top of the highlight color).
CHAMELEON_FALLBACK = "#3daee9"   # Breeze highlight, used outside of Plasma
BACK_SHADE = ("#000000", 0.18)
EMBLEM_SHADE = ("#ffffff", 0.55)

FILL_RE = re.compile(r"fill:(rgb\([^)]*\)|#[0-9a-fA-F]{6})")
ELEM_RE = re.compile(r"<(path|rect|circle|ellipse|polygon)\b[^>]*/>", re.S)


def rgb_to_hex(s):
    m = re.match(r"rgb\(([\d.]+)%,([\d.]+)%,([\d.]+)%\)", s)
    if not m:
        return s.upper()
    return "#%02X%02X%02X" % tuple(round(float(v) * 2.55) for v in m.groups())


def template_colors(color):
    """Return (back, front) hex colors from folder-<color>.svg, in path order."""
    with open(os.path.join(TEMPLATE_DIR, "folder-%s.svg" % color)) as f:
        svg = f.read()
    seen = []
    for c in FILL_RE.findall(svg):
        h = rgb_to_hex(c)
        if h not in ("#000000", "#FFFFFF") and h not in seen:
            seen.append(h)
    if len(seen) != 2:
        sys.exit("unexpected palette in folder-%s.svg: %s" % (color, seen))
    return seen[0], seen[1]


def recolor_fixed(svg, mapping):
    for old, new in mapping.items():
        svg = svg.replace("fill:" + old, "fill:" + new)
    return svg


def recolor_chameleon(svg):
    if not any(c in svg for c in (BLUE_BACK, BLUE_FRONT, BLUE_EMBLEM)):
        return svg

    def repl(m):
        el = m.group(0)
        fm = FILL_RE.search(el)
        if not fm or fm.group(1) not in (BLUE_BACK, BLUE_FRONT, BLUE_EMBLEM):
            return el
        col = fm.group(1)
        base = el.replace("fill:" + col, "fill:currentColor", 1)
        base = re.sub(r"<(\w+)", r'<\1 class="ColorScheme-Highlight"', base, count=1)
        shade = {BLUE_BACK: BACK_SHADE, BLUE_EMBLEM: EMBLEM_SHADE}.get(col)
        if not shade:
            return base
        over = re.sub(r'\sid="[^"]*"', "", el)
        over = over.replace("fill:" + col, "fill:" + shade[0], 1)
        over = re.sub(r"fill-opacity:[\d.]+", "fill-opacity:%g" % shade[1], over)
        if "fill-opacity" not in over:
            over = over.replace("fill:" + shade[0], "fill:%s;fill-opacity:%g" % shade, 1)
        return base + "\n" + over

    svg = ELEM_RE.sub(repl, svg)
    style = ('<defs><style id="current-color-scheme" type="text/css">'
             ".ColorScheme-Highlight { color:%s; }</style></defs>" % CHAMELEON_FALLBACK)
    svg = re.sub(r"(<svg\b[^>]*>)", r"\1\n" + style, svg, count=1)
    for c in (BLUE_BACK, BLUE_FRONT, BLUE_EMBLEM):
        if c in svg:
            raise ValueError("unconverted color %s" % c)
    return svg


def build_variant(name, base, transform):
    dst = os.path.join(ROOT, name)
    if os.path.lexists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for d in SHARED_DIRS:
        os.symlink("../%s/%s/" % (base, d), os.path.join(dst, d))
    for link, target in SHARED_LINKS.items():
        os.symlink(target, os.path.join(dst, link))
    shutil.copytree(os.path.join(ROOT, base, "places"), os.path.join(dst, "places"),
                    symlinks=True)
    for f in ("LICENSE", "README.md"):
        if os.path.exists(os.path.join(ROOT, base, f)):
            shutil.copy2(os.path.join(ROOT, base, f), dst)
    with open(os.path.join(ROOT, base, "index.theme")) as f:
        theme = f.read()
    theme = re.sub(r"^Name=.*$", "Name=" + name, theme, count=1, flags=re.M)
    with open(os.path.join(dst, "index.theme"), "w") as f:
        f.write(theme)

    changed = 0
    for root, _, files in os.walk(os.path.join(dst, "places")):
        for fn in files:
            p = os.path.join(root, fn)
            if os.path.islink(p) or not fn.endswith(".svg") or TEMPLATE_RE.match(fn):
                continue
            with open(p) as f:
                svg = f.read()
            new = transform(svg)
            if new != svg:
                with open(p, "w") as f:
                    f.write(new)
                changed += 1
    print("%-36s %4d icons recolored" % (name, changed))


def main():
    if "--clean" in sys.argv:
        for d in os.listdir(ROOT):
            if d.startswith("Newaita-reborn-") and d not in BASES.values():
                shutil.rmtree(os.path.join(ROOT, d))

    for color in sorted(EMBLEM):
        back, front = template_colors(color)
        mapping = {BLUE_BACK: back, BLUE_FRONT: front, BLUE_EMBLEM: EMBLEM[color]}
        mapping.update(EXTRA.get(color, {}))
        for suffix, base in BASES.items():
            build_variant("Newaita-reborn-%s%s" % (color, suffix), base,
                          lambda s, m=mapping: recolor_fixed(s, m))

    for suffix, base in BASES.items():
        build_variant("Newaita-reborn-chameleon%s" % suffix, base, recolor_chameleon)


if __name__ == "__main__":
    main()
