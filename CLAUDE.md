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

## Data Migration — CRITICAL

When adding new fields to habits or any persisted data structure, ALWAYS add a migration in the App component's `useState` initializer AND in the `init` async function. Without this, existing user data loaded from GitHub or localStorage will be missing the new fields and behave incorrectly.

**The migration pattern** (inside the `init` function's `migrate` helper):
```js
const migrate = h => {
  const def = INIT_HABITS.find(x => x.id === h.id);
  return {
    ...h,
    newField: h.newField ?? def?.newField ?? defaultValue,
    // always use ?? to preserve existing data and only fill gaps
  };
};
```

**Rules:**
- Never overwrite existing user data — use `??` (nullish coalescing), not `||`
- Always backfill from `INIT_HABITS` defaults when a field is missing
- Test by checking that `completedDates`, `days`, `goalCat`, `duration` etc. survive code updates
- The migration runs in two places: the `useState` initializer (for localStorage) and the `init` useEffect (for GitHub data)
- `name` and `isNN` fields are intentionally synced from `INIT_HABITS` to fix renames/promotions across code versions — this is an exception to the "don't overwrite" rule

## Sync Architecture

- **Cloudflare Worker** (`https://datatoken.ran-varsano.workers.dev`) handles all GitHub writes — no token needed in the browser
- Worker endpoints: `POST /sync` (write file), `GET /read?file=X` (read file bypassing CDN cache)
- `GITHUB_TOKEN` stored as secret in Cloudflare Worker settings — never in the browser
- `habits.json`, `books.json`, `reviews.json` all sync to `DeVers-goat/morning-habits` repo
- Reading uses `raw.githubusercontent.com` with cache-busting `?_=timestamp`
- Polling every 10 seconds + immediate pull on tab focus/visibility change
