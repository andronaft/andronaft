#!/usr/bin/env python3
"""Generate assets/cards/<repo>.svg: repository pin cards in the github-readme-stats "tokyonight" look,
rendered locally so they never depend on a third-party service being up.

Usage:  GH_TOKEN=... python3 scripts/gen_cards.py          (uses the gh CLI for the API call)
"""

import json, subprocess, textwrap
from pathlib import Path
from xml.sax.saxutils import escape

OWNER = "andronaft"
REPOS = ["k8s-guardian", "health-os", "Logbeam", "FileForge"]
OUT = Path("assets/cards")

W = 400
TITLE, ICON, TEXT, BG = "#70a5fd", "#bf91f3", "#38bdae", "#1a1b27"
FONT = "'Segoe UI', Ubuntu, Sans-Serif"
LINE_CHARS, MAX_LINES, LINE_H = 52, 3, 16

ICONS = {
    "repo": "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 1 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 0 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 0 1 1-1h8zM5 12.25v3.25a.25.25 0 0 0 .4.2l1.45-1.087a.25.25 0 0 1 .3 0L8.6 15.7a.25.25 0 0 0 .4-.2v-3.25a.25.25 0 0 0-.25-.25h-3.5a.25.25 0 0 0-.25.25z",
    "star": "M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z",
    "fork": "M5 3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v.878A2.25 2.25 0 005.75 8.5h1.5v2.128a2.251 2.251 0 101.5 0V8.5h1.5a2.25 2.25 0 002.25-2.25v-.878a2.25 2.25 0 10-1.5 0v.878a.75.75 0 01-.75.75h-4.5A.75.75 0 015 6.25v-.878zm3.75 7.378a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm3-8.75a.75.75 0 100-1.5.75.75 0 000 1.5z",
}


def fetch():
    q = "query($owner:String!){" + " ".join(
        f'r{i}: repository(owner:$owner, name:"{name}"){{ name description stargazerCount forkCount primaryLanguage{{ name color }} }}'
        for i, name in enumerate(REPOS)) + "}"
    out = subprocess.run(["gh", "api", "graphql", "-f", f"owner={OWNER}", "-f", f"query={q}"], check=True, capture_output=True, text=True).stdout
    data = json.loads(out)["data"]
    return [data[f"r{i}"] for i in range(len(REPOS))]


def wrap(desc):
    lines = textwrap.wrap(desc or "", LINE_CHARS)
    if len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]
        lines[-1] = lines[-1][:LINE_CHARS - 3].rstrip(" ,.;:") + "..."
    return lines or ["No description"]


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def card(repo):
    lines = wrap(repo["description"])
    lang = repo.get("primaryLanguage") or {}
    h = 60 + LINE_H * len(lines) + 30
    desc = "".join(f'<tspan x="25" dy="{0 if i == 0 else LINE_H}">{escape(l)}</tspan>' for i, l in enumerate(lines))
    meta_y = h - 24
    parts, x = [], 25
    if lang:
        parts.append(f'<g transform="translate({x},{meta_y})"><circle cx="5" cy="-4" r="6" fill="{lang["color"]}"/><text x="18" class="gray">{escape(lang["name"])}</text></g>')
        x += 18 + 7 * len(lang["name"]) + 22
    for key, val in (("star", repo["stargazerCount"]), ("fork", repo["forkCount"])):
        if key == "fork" and not val:
            continue
        parts.append(f'<g transform="translate({x},{meta_y})"><svg class="icon" y="-12" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="{ICONS[key]}"/></svg><text x="22" class="gray">{fmt(val)}</text></g>')
        x += 22 + 8 * len(fmt(val)) + 22
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" fill="none" role="img" aria-labelledby="t">
<title id="t">{escape(repo["name"])}: {escape(repo["description"] or "")}</title>
<style>
.header {{ font: 600 18px {FONT}; fill: {TITLE}; }}
.description {{ font: 400 13px {FONT}; fill: {TEXT}; }}
.gray {{ font: 400 12px {FONT}; fill: {TEXT}; }}
.icon {{ fill: {ICON}; }}
</style>
<rect x="0.5" y="0.5" rx="4.5" width="{W - 1}" height="{h - 1}" fill="{BG}" stroke="{BG}"/>
<g transform="translate(25,35)">
  <svg class="icon" x="0" y="-13" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="{ICONS["repo"]}"/></svg>
  <text x="25" y="0" class="header">{escape(repo["name"])}</text>
</g>
<text x="25" y="65" class="description">{desc}</text>
{"".join(parts)}
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for repo in fetch():
        (OUT / f"{repo['name']}.svg").write_text(card(repo), encoding="utf-8")
        print(repo["name"], repo["stargazerCount"], "stars")
