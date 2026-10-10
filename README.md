# Pricing roles tracker

Tracks pricing, monetization and RGM roles in Canada and Colombia, and what each company's hiring
suggests about its pricing strategy. Runs Monday to Friday at 20:00 on the Mac mini, publishes a
dashboard on GitHub Pages, and sends an ntfy alert only when a new Canada or Colombia role appears.

## How a run works

| Step | What runs | AI? |
|---|---|---|
| 1. Recheck every known job link (Workday, Greenhouse, SmartRecruiters APIs, else the page) | `scripts/recheck.py` | No |
| 2. Search for new roles, official links, strategy notes, named posters | Claude Code (`agent/discovery_prompt.md`) | Yes |
| 3. Merge Claude's proposal: IDs, de-duplication, repost linking | `scripts/apply_proposals.py` | No |
| 4. Check the links of roles found today | `scripts/recheck.py --new-only` | No |
| 5. Integrity rules; any failure stops the run | `scripts/validate.py` | No |
| 6. Commit and push; GitHub validates again and publishes the dashboard | `.github/workflows/pages.yml` | No |
| 7. Alert for new Canada/Colombia roles; failures go to a separate quiet topic | `scripts/notify.py` | No |

Claude can only write one file, `proposals/YYYY-MM-DD.json`. It cannot edit the data, run
commands, or set verification dates. Only the recheck script can mark a role verified, and only
after a positive check that is logged in `data/checks.jsonl`. Git history is the audit trail.

## One-time setup on the Mac mini

1. **Create the GitHub repo.** On github.com, create a public repository named `pricing-intel`
   with no README. Then go to Settings, Pages, and set Source to "GitHub Actions".

2. **Put this folder on the Mac and push it.**
   ```bash
   cd ~/pricing-intel
   git init -b main && git add -A && git commit -m "Baseline 2026-10-10"
   git remote add origin https://github.com/YOUR-USERNAME/pricing-intel.git
   git push -u origin main
   ```
   If the push asks for credentials, run `brew install gh && gh auth login` first.
   Within a couple of minutes the dashboard is live at `https://YOUR-USERNAME.github.io/pricing-intel/`.

3. **Install Claude Code and sign in with your subscription.**
   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   claude auth login
   claude update          # needs v2.1.259 or later
   ```

4. **Make two ntfy topics.** Generate two random names:
   ```bash
   python3 -c "import secrets; print('pricing-' + secrets.token_hex(6)); print('pricing-' + secrets.token_hex(6))"
   ```
   In the ntfy iPhone app, subscribe to both on ntfy.sh: the first for new roles, the second for problems.

5. **Fill in the config.**
   ```bash
   cp config.example.env config.env
   open -e config.env     # paste the two topics and your dashboard address
   ```

6. **Test the parts.**
   ```bash
   python3 scripts/validate.py                       # should pass
   python3 scripts/recheck.py --dry-run              # real link checks, nothing saved
   set -a; source config.env; set +a
   python3 scripts/notify.py --fail "Test alert"     # your phone should buzz (problems topic)
   ```

7. **Turn on the schedule and run once now.**
   ```bash
   bash scripts/install_mac.sh --run-now
   tail -f logs/$(date +%F).log
   ```
   A full run takes about 10 to 30 minutes, mostly Claude searching.

8. **Keep the Mac awake and signed in.** In System Settings, under Energy, turn on "Prevent
   automatic sleeping". Claude's sign-in is stored in the Keychain, which is only available while
   your user is logged in. After a power cut, log in once or the run fails (and you get a problem alert).

## Day to day

- **Logs:** `logs/YYYY-MM-DD.log` on the Mac. Claude's raw output is in `.run/`.
- **Run manually:** `launchctl kickstart gui/$(id -u)/com.pricingintel.daily`
- **Pause:** `launchctl bootout gui/$(id -u)/com.pricingintel.daily`. To resume, run `bash scripts/install_mac.sh`.
- **Change the time:** edit the `Hour` and `Minute` values in `launchd/com.pricingintel.daily.plist`, then run `bash scripts/install_mac.sh`.
- **Edit data by hand:** change the JSON in `data/`, run `python3 scripts/validate.py`, then commit and push.
- **If Claude's sign-in keeps expiring:** run `claude setup-token` to create a long-lived token
  for scripts, and add it to `config.env` as `CLAUDE_CODE_OAUTH_TOKEN=...` (see the Claude Code
  authentication docs).
- **Usage:** each run uses your Claude plan's usage. To use a pay-per-use API key instead, run
  `claude auth login --console`.

## Status meanings

- **Verified open:** the employer's own posting was checked and open on that date.
- **Unverified:** found but not confirmed (LinkedIn-only, aggregator-only, blocked or erroring).
  It is never treated as closed.
- **Removed:** the posting returned "not found" on two separate runs. The removal date is the first time that was seen.
- **Closed:** the source explicitly says it no longer accepts applications.

LinkedIn is never checked automatically. A role whose only link is LinkedIn stays unverified until
an official posting is found. The discovery step looks for official postings on every run.
