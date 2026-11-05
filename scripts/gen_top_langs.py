#!/usr/bin/env python3
"""Generate assets/top-langs.svg: the "Top languages" card.

Sums language bytes over the owner's public, non-fork repositories
(GitHub GraphQL via the gh CLI) and draws a compact card, so the
profile does not depend on an outside card service.

Usage:  OWNER=andronaft LIMIT=8 python3 scripts/gen_top_langs.py
"""

import json
import os
import subprocess
from html import escape
from pathlib import Path

OWNER = os.environ.get("OWNER", "andronaft")
LIMIT = int(os.environ.get("LIMIT", "8"))
OUT = Path("assets/top-langs.svg")

BG = "#1a1b27"
TITLE = "#70a5fd"
TEXT = "#38bdae"
FALLBACK = "#858585"

QUERY = """
query($owner: String!) {
  user(login: $owner) {
    repositories(first: 100, privacy: PUBLIC, isFork: false, ownerAffiliations: OWNER) {
      nodes { languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
        edges { size node { name color } } } }
    }
  }
}"""


def fetch():
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"owner={OWNER}", "-f", f"query={QUERY}"],
        check=True, capture_output=True, text=True,
    ).stdout
    totals, colors = {}, {}
    for repo in json.loads(out)["data"]["user"]["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            totals[name] = totals.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or FALLBACK
    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:LIMIT]
    total = sum(size for _, size in top) or 1
    return [(name, size * 100 / total, colors[name]) for name, size in top]


def render(langs):
    width, pad = 300, 25
    bar_w = width - 2 * pad
    rows = (len(langs) + 1) // 2
    height = 90 + rows * 25

    bar, x = [], 0.0
    for _, pct, color in langs:
        w = bar_w * pct / 100
        bar.append(f'<rect x="{x:.2f}" y="0" width="{w:.2f}" height="8" fill="{color}"/>')
        x += w

    items = []
    for i, (name, pct, color) in enumerate(langs):
        cx = 0 if i % 2 == 0 else 150
        cy = (i // 2) * 25
        items.append(
            f'<g transform="translate({cx},{cy})">'
            f'<circle cx="5" cy="6" r="5" fill="{color}"/>'
            f'<text x="15" y="10" class="lang">{escape(name)} {pct:.2f}%</text></g>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Most used languages">
<style>
.title {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {TITLE}; }}
.lang {{ font: 400 11px 'Segoe UI', Ubuntu, sans-serif; fill: {TEXT}; }}
</style>
<rect width="{width}" height="{height}" rx="4.5" fill="{BG}"/>
<text x="{pad}" y="35" class="title">Most Used Languages</text>
<defs><clipPath id="bar"><rect width="{bar_w}" height="8" rx="5"/></clipPath></defs>
<g transform="translate({pad},55)" clip-path="url(#bar)">{''.join(bar)}</g>
<g transform="translate({pad},80)">{''.join(items)}</g>
</svg>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(fetch()), encoding="utf-8")
    print(f"wrote {OUT}")
