#!/usr/bin/env bash
# Rewrites the block between LATEST:START and LATEST:END in README.md
# with the most recent releases of the owner's public repositories.
set -euo pipefail
OWNER="${OWNER:-andronaft}"
LIMIT="${LIMIT:-5}"

list=$(gh api graphql -f owner="$OWNER" -f query='
query($owner: String!) {
  user(login: $owner) {
    repositories(first: 100, privacy: PUBLIC, isFork: false, ownerAffiliations: OWNER) {
      nodes { name releases(first: 5, orderBy: {field: CREATED_AT, direction: DESC}) {
        nodes { tagName publishedAt url isDraft isPrerelease } } }
    }
  }
}' --jq '[.data.user.repositories.nodes[] | .name as $r | .releases.nodes[]
          | select(.isDraft | not) | {repo: $r, tag: .tagName, ts: .publishedAt, date: .publishedAt[:10], url: .url}]
        | sort_by(.ts) | reverse | .['":$LIMIT"'][]
        | "- 🚀 **[\(.repo) \(.tag)](\(.url))** · \(.date)"')

python3 - "$list" <<'PY'
import re, sys
block = sys.argv[1].strip() or "- nothing released yet"
readme = open("README.md", encoding="utf-8").read()
new = re.sub(r"(<!-- LATEST:START -->).*?(<!-- LATEST:END -->)",
             lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}", readme, flags=re.S)
open("README.md", "w", encoding="utf-8").write(new)
PY
