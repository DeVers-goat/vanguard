# RanClaude Project

Two standalone single-file React apps + a GitHub Actions automation.

## Apps

### `Main` — Vanguard habit/goals/books tracker
- Standalone React app, no build tools, opened via `index.html`
- Served by React 18 + Babel Standalone from CDN
- All state in `localStorage`:
  - `vg_habits` — habits array
  - `vg_google_api_key`, `vg_google_client_id` — Google Calendar sync
- Habits auto-export to `habits.json` via File System Access API (tap the 📲 button on Habits screen)

### `Library` — Book library with AI summaries
- Uses Open Library API for book search (not Google Books)
- Uses Groq API (llama-3.3-70b-versatile) for AI-generated summaries
- API key stored in `localStorage` under `lib_gemini_key` (name kept from Gemini days)
- Books persist in `localStorage` under `lib_my_books`

## Morning WhatsApp Reminder — Automation

Runs daily at 9:00 AM Israel time without the PC being on:

1. **cron-job.org** triggers GitHub Actions at 9am Israel (via GitHub API dispatch)
2. **GitHub Actions** (`.github/workflows/morning-habits.yml`) runs `send_reminder.py`
3. **send_reminder.py** reads `habits.json`, formats the message, calls Twilio API
4. **Twilio WhatsApp Sandbox** delivers the message (sandbox session expires after 72hrs of inactivity — rejoin by messaging the sandbox number)

GitHub repo: `DeVers-goat/morning-habits`

Secrets stored in GitHub repo settings: `TWILIO_SID`, `TWILIO_TOKEN`

Local `c:\RanClaude\whatsapp-habits.ps1` is a manual test script; the matching Windows Task Scheduler task ("Morning Habit Reminder") is disabled since GitHub handles the schedule.

## Conventions

- No build tools anywhere. Edits go directly into the single-file app.
- Files with no extension (`Main`, `Library`) are JSX — edit them like any React file.
- All styles live in a `<style>` block inside the file's `_st.textContent`.
- When adding new CSS animations, put them in that block alongside existing keyframes.
