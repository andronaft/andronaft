#!/usr/bin/env python3
"""Generate assets/marquee.svg: a metro-style LED dot-matrix marquee.

The text is rendered with a 5x7 pixel font onto a dot grid and scrolled
right-to-left with SMIL animation (works inside <img> on GitHub).

Usage:  python3 scripts/gen_marquee.py
"""

from pathlib import Path

TEXT = (
    "Hi, I'm Andrii \U0001F44B"
    "  ◆  I build guardrails for Kubernetes"
    "  ◆  MCP servers for AI agents"
    "  ◆  and tools that make logs readable again"
)

COLS = 104         # visible columns of the display
ROWS = 7           # font height
PAD_ROWS = 1       # off-dots padding above/below the text
PAD_COLS = 1       # off-dots padding left/right
BEZEL = 0.6        # dark frame around the dot grid, in cells
STEPS_PER_SEC = 48 # scroll speed

LIT = "#ffb13b"
CORE = "#ffd27a"
GLOW = "#ff8a00"
OFF = "#2b1a08"
BG = "#0a0a0b"
BEZEL_COLOR = "#17171a"

# 5x7 font, '#' = lit. Glyphs are trimmed to their used columns
# (proportional spacing), 1 blank column between glyphs.
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    "b": ["#....", "#....", "#.##.", "##..#", "#...#", "#...#", "####."],
    "c": [".....", ".....", ".###.", "#....", "#....", "#...#", ".###."],
    "d": ["....#", "....#", ".##.#", "#..##", "#...#", "#...#", ".####"],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "f": ["..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."],
    "g": [".....", ".####", "#...#", "#...#", ".####", "....#", ".###."],
    "h": ["#....", "#....", "#.##.", "##..#", "#...#", "#...#", "#...#"],
    "i": ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
    "j": ["...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."],
    "k": ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
    "l": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#...#", "#...#"],
    "n": [".....", ".....", "#.##.", "##..#", "#...#", "#...#", "#...#"],
    "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    "p": [".....", "####.", "#...#", "#...#", "####.", "#....", "#...."],
    "q": [".....", ".####", "#...#", "#...#", ".####", "....#", "....#"],
    "r": [".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."],
    "s": [".....", ".....", ".###.", "#....", ".###.", "....#", "####."],
    "t": [".#...", ".#...", "###..", ".#...", ".#...", ".#..#", "..##."],
    "u": [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"],
    "v": [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "w": [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
    "x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    "y": [".....", ".....", "#...#", "#...#", ".####", "....#", ".###."],
    "z": [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
    ",": [".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    "'": [".##..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "&": [".##..", "#..#.", "#..#.", ".##..", "#.#.#", "#..#.", ".##.#"],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "/": [".....", "....#", "...#.", "..#..", ".#...", "#....", "....."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    # separator diamond
    "◆": [".....", "..#..", ".###.", "#####", ".###.", "..#..", "....."],
    # waving hand
    "\U0001F44B": [
        ".#.#.#.",
        ".#.#.#.",
        ".######",
        "#.#####",
        ".######",
        ".#####.",
        "..####.",
    ],
}


def trim(glyph):
    """Drop fully blank leading/trailing columns (keep spaces as-is)."""
    width = len(glyph[0])
    used = [c for c in range(width) if any(row[c] == "#" for row in glyph)]
    if not used:
        return glyph
    lo, hi = used[0], used[-1] + 1
    return [row[lo:hi] for row in glyph]


def render(text):
    """Return list of (col, row) lit cells and total width in columns."""
    cells = []
    x = 0
    for ch in text:
        if ch not in FONT:
            raise SystemExit(f"no glyph for {ch!r} (U+{ord(ch):04X})")
        glyph = trim(FONT[ch])
        assert len(glyph) == ROWS, ch
        for r, row in enumerate(glyph):
            for c, px in enumerate(row):
                if px == "#":
                    cells.append((x + c, r))
        x += len(glyph[0]) + 1
    return cells, x - 1


def main():
    cells, text_w = render(TEXT)

    grid_w = COLS + 2 * PAD_COLS
    grid_h = ROWS + 2 * PAD_ROWS
    W = grid_w + 2 * BEZEL
    H = grid_h + 2 * BEZEL
    gx, gy = BEZEL, BEZEL                      # grid origin
    tx0, ty0 = gx + PAD_COLS, gy + PAD_ROWS    # text row origin

    # Text starts just off the right edge and scrolls until fully off the left.
    steps = COLS + text_w
    dur = steps / STEPS_PER_SEC
    values = ";".join(str(-i) for i in range(steps + 1))

    # Lit cells as one path of unit squares; the circle mask turns them into dots.
    d = "".join(f"M{tx0 + COLS + c} {ty0 + r}h1v1h-1z" for c, r in cells)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W:g} {H:g}" width="{W * 10:g}" height="{H * 10:g}" shape-rendering="geometricPrecision">
<title>{TEXT}</title>
<defs>
  <pattern id="dot" width="1" height="1" patternUnits="userSpaceOnUse">
    <circle cx="0.5" cy="0.5" r="0.4" fill="#fff"/>
  </pattern>
  <pattern id="dotoff" width="1" height="1" patternUnits="userSpaceOnUse">
    <circle cx="0.5" cy="0.5" r="0.4" fill="{OFF}"/>
  </pattern>
  <mask id="grid" maskUnits="userSpaceOnUse" x="0" y="0" width="{W:g}" height="{H:g}">
    <rect x="{gx:g}" y="{gy:g}" width="{grid_w}" height="{grid_h}" fill="url(#dot)"/>
  </mask>
  <clipPath id="board"><rect x="{gx:g}" y="{gy:g}" width="{grid_w}" height="{grid_h}"/></clipPath>
  <filter id="glow" filterUnits="userSpaceOnUse" x="{gx:g}" y="{gy:g}" width="{grid_w}" height="{grid_h}">
    <feGaussianBlur stdDeviation="0.55"/>
  </filter>
  <path id="txt" d="{d}"/>
  <g id="lit" mask="url(#grid)">
    <g>
      <animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{values}" dur="{dur:.3f}s" repeatCount="indefinite"/>
      <use xlink:href="#txt" href="#txt" fill="{LIT}"/>
    </g>
  </g>
</defs>
<rect width="{W:g}" height="{H:g}" rx="0.8" fill="{BEZEL_COLOR}"/>
<rect x="{gx - 0.35:g}" y="{gy - 0.35:g}" width="{grid_w + 0.7:g}" height="{grid_h + 0.7:g}" rx="0.4" fill="{BG}"/>
<rect x="{gx:g}" y="{gy:g}" width="{grid_w}" height="{grid_h}" fill="url(#dotoff)"/>
<g clip-path="url(#board)">
  <use xlink:href="#lit" href="#lit" filter="url(#glow)" opacity="0.9"/>
  <use xlink:href="#lit" href="#lit"/>
</g>
</svg>
"""
    out = Path(__file__).resolve().parent.parent / "assets" / "marquee.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(svg)
    print(f"{out}: {len(svg)} bytes, {len(cells)} dots, {text_w} cols, {steps} steps, {dur:.1f}s loop")


if __name__ == "__main__":
    main()
