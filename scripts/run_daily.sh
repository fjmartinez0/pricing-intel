#!/bin/bash
# Daily pipeline, started by launchd Monday to Friday at 2:30 a.m. (Mac local time).
# Steps: pull, recheck known links, Claude discovery, merge, verify new links,
# validate, commit and push (GitHub publishes the dashboard), alert.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
export PATH="/Library/Frameworks/Python.framework/Versions/Current/bin:$HOME/.local/bin:$HOME/.claude/local:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
set -a; source "$REPO/config.env"; set +a

TODAY="$(TZ=America/Toronto date +%F)"
mkdir -p logs .run
LOG="logs/$TODAY.log"
exec >>"$LOG" 2>&1
echo "=== Run started $(date) ==="

STEP="startup"
LOCK="$REPO/.run/lock"
fail() {
  python3 scripts/notify.py --fail "Run failed at step: $STEP. Check logs/$TODAY.log on the Mac mini." || true
  rm -rf "$LOCK"
  exit 1
}
trap fail ERR
mkdir "$LOCK" 2>/dev/null || { echo "Another run is in progress"; exit 0; }

STEP="git pull"
git pull --ff-only --quiet
BASE="$(git rev-parse HEAD)"
cp data/opportunities.json .run/before.json

STEP="recheck known links"
python3 scripts/recheck.py

STEP="Claude login check"
claude auth status >/dev/null

STEP="Claude discovery"
WEEKDAY="$(TZ=America/Toronto date +%u)"
PROMPT="$(sed -e "s/{{TODAY}}/$TODAY/g" -e "s/{{WEEKDAY}}/$WEEKDAY/g" agent/discovery_prompt.md)"
claude -p "$PROMPT" \
  --model "${CLAUDE_MODEL:-opus}" \
  --tools "WebSearch,WebFetch,Read,Write,Edit,Glob,Grep" \
  --allowedTools "WebSearch,WebFetch,Read,Glob,Grep,Edit(./proposals/**)" \
  --permission-mode dontAsk \
  --permission-prompts none \
  --max-turns "${CLAUDE_MAX_TURNS:-250}" \
  --no-session-persistence \
  --output-format json > ".run/claude_$TODAY.json" || echo "Claude exited with code $? (continuing if a proposal was written)"

STEP="read Claude proposal"
test -s "proposals/$TODAY.json"
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "proposals/$TODAY.json"

STEP="coverage check"
python3 scripts/coverage_check.py "proposals/$TODAY.json"

STEP="merge proposal"
python3 scripts/apply_proposals.py "proposals/$TODAY.json"

STEP="verify new links"
python3 scripts/recheck.py --new-only

STEP="validate data"
python3 scripts/validate.py --base-ref "$BASE"

STEP="record run time"
python3 -c 'import sys; sys.path.insert(0, "scripts"); import common as c; from datetime import datetime
m = c.load("meta.json"); m["last_run_at"] = datetime.now(c.TZ).isoformat(timespec="seconds"); c.save("meta.json", m)'

STEP="commit and push"
git add data "proposals/$TODAY.json"
if ! git diff --cached --quiet; then
  git commit --quiet -m "Daily update $TODAY"
  git push --quiet
fi

STEP="send alert"
python3 scripts/notify.py --before .run/before.json --after data/opportunities.json

rm -rf "$LOCK"
echo "=== Run finished $(date) ==="
