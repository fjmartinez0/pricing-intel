#!/bin/bash
# One-time setup on the Mac mini: installs the weekday 20:00 launchd job.
# Usage: bash scripts/install_mac.sh            install or reinstall the schedule
#        bash scripts/install_mac.sh --run-now  also start one run immediately (for testing)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.pricingintel.daily"
DEST="$HOME/Library/LaunchAgents/$LABEL.plist"

[ -f "$REPO/config.env" ] || { echo "Missing config.env. Run: cp config.example.env config.env and fill it in."; exit 1; }
command -v claude >/dev/null || { echo "Claude Code not found. Install it first (see README)."; exit 1; }
claude auth status >/dev/null || { echo "Claude Code is not signed in. Run: claude auth login"; exit 1; }
git -C "$REPO" remote get-url origin >/dev/null || { echo "No GitHub remote set for this folder."; exit 1; }

mkdir -p "$REPO/logs" "$HOME/Library/LaunchAgents"
chmod +x "$REPO/scripts/run_daily.sh"
sed "s#__REPO__#$REPO#g" "$REPO/launchd/$LABEL.plist" > "$DEST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$DEST"
echo "Scheduled: Monday to Friday at 20:00 (this Mac's local time)."

if [ "${1:-}" = "--run-now" ]; then
  launchctl kickstart "gui/$(id -u)/$LABEL"
  echo "Test run started. Follow it with: tail -f $REPO/logs/\$(date +%F).log"
fi
