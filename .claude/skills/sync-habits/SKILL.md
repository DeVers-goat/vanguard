---
name: sync-habits
description: Commit habits.json changes from the working directory to the DeVers-goat/morning-habits GitHub repo so the morning WhatsApp reminder picks them up
---

# Sync Habits to GitHub

When the user invokes this skill:

1. Check if `c:\RanClaude\habits.json` exists — if not, tell the user to tap the 📲 button on the Habits screen in the Main app first.

2. Check `git status` for changes to `habits.json` in `c:\RanClaude`:
   - If no changes, say "habits.json is already in sync with GitHub" and stop.
   - If there are changes, proceed.

3. Run these git commands in order from `c:\RanClaude`:
   ```
   git add habits.json
   git commit -m "Update habits"
   git push
   ```

4. Report the commit hash and confirm that the daily WhatsApp reminder will now reflect the updated habits.

## Notes
- The repo is `DeVers-goat/morning-habits` (already configured as remote `origin`)
- Only commit `habits.json` — don't accidentally commit other files
- If push fails due to network, retry once before reporting the error
