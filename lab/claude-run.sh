#!/usr/bin/env bash
# The Claude arm of the disclosure lab, through a real MCP server.
#
# Each trial is a fresh headless Claude session that has exactly one tool: the case's tool, served by
# tools/lab/mcp-stub/server.mjs with the description from the version under test. It runs in an empty
# temporary directory with every built-in tool off (--tools ""), no skills or slash commands, no MCP server
# but the lab's (--strict-mcp-config), and no user or local settings (--setting-sources project). The
# session's own startup report, which lists the tools it had, is kept on every row as proof.
#
# Why so strict (8 Oct 2026): the first pass ran inside the working repository and its sessions read the lab
# itself; then the sign-in check, run with every tool, read the repository's instructions and messaged another
# session.
#
# Needs the CLI signed in once (it uses the plan, not an API key):
#   claude          # then /login
# Then:
#   cd <repo> && tools/lab/claude-run.sh <trials> [model] [case-id]
set -uo pipefail
TRIALS=${1:-5}
MODEL=${2:-}
ONLY=${3:-}
ROOT=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-"$ROOT/runs/final/$(date +%Y-%m-%dT%H%M)-claude-${MODEL:-default}${ONLY:+-$ONLY}.jsonl"}
mkdir -p "$(dirname "$OUT")"
SANDBOX=$(mktemp -d -t lab-subject-XXXX)
CALLS=$(mktemp -t lab-calls-XXXX)
CFG=$(mktemp -t lab-mcp-XXXX)
trap 'rm -rf "$SANDBOX" "$CALLS" "$CFG"' EXIT
LOCKDOWN=(--tools "" --strict-mcp-config --disable-slash-commands --setting-sources project)

command -v claude >/dev/null || { echo "the claude CLI is not installed"; exit 2; }
probe=$(cd "$SANDBOX" && claude -p "Reply with the word ok." "${LOCKDOWN[@]}" ${MODEL:+--model "$MODEL"} \
          --output-format json < /dev/null 2>/dev/null | python3 -c "import sys,json
try: print(json.load(sys.stdin).get('result',''))
except Exception: print('no answer')")
case "$probe" in *"Not logged in"*|*"no answer"*)
  echo "the claude CLI is not signed in: run 'claude' once in a terminal and use /login"; exit 3;;
esac

touch "$OUT"
COMMIT=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)
python3 "$ROOT/write-env.py" "$OUT" "$TRIALS" "${MODEL:-default}" "$ROOT"

while IFS=$'\t' read -r case_id tool task case_ver case_sha; do
  [ -n "$ONLY" ] && [ "$ONLY" != "$case_id" ] && continue
  for variant in before after; do
    printf '{"mcpServers":{"lab":{"command":"node","args":["%s/mcp-stub/server.mjs"],"env":{"LAB_CASE":"%s","LAB_VARIANT":"%s","LAB_LOG":"%s"}}}}\n' \
      "$ROOT" "$case_id" "$variant" "$CALLS" > "$CFG"
    for i in $(seq 1 "$TRIALS"); do
      : > "$CALLS"
      STARTED=$(date -u +%Y-%m-%dT%H:%M:%SZ)
      ( cd "$SANDBOX" && claude -p "$task" "${LOCKDOWN[@]}" \
          --mcp-config "$CFG" --allowedTools "mcp__lab__$tool" \
          --append-system-prompt "When the work is done, answer the person directly in plain language. Do not narrate your own process." \
          ${MODEL:+--model "$MODEL"} \
          --output-format stream-json --verbose < /dev/null 2>/dev/null ) \
      | CASE="$case_id" VARIANT="$variant" TRIAL="$i" STARTED="$STARTED" COMMIT="$COMMIT" \
        CASE_VER="$case_ver" CASE_SHA="$case_sha" CALLS="$CALLS" ASKED="${MODEL:-default}" \
        python3 "$ROOT/record-trial.py" >> "$OUT"
      echo "$case_id $variant $i"
    done
  done
done < <(python3 -c "
import json
for c in json.load(open('$ROOT/cases.json')):
    print(c['id'], c['tool']['name'], c['user_task'].replace(chr(9), ' '), c.get('version', 1), c.get('sha', ''), sep=chr(9))")

echo
"$ROOT/score.py" "$OUT"
