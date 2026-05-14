import json, urllib.request, urllib.parse, os, datetime

with open('habits.json', encoding='utf-8-sig') as f:
    habits = json.load(f)

israel = datetime.timezone(datetime.timedelta(hours=3))
now = datetime.datetime.now(israel)
js_dow = (now.weekday() + 1) % 7

def prev_date(n=1):
    d = now - datetime.timedelta(days=n)
    return d.strftime('%Y-%m-%d')

today_habits = [h for h in habits if js_dow in (h.get('days') or [])]
pending = [h for h in today_habits if h.get('status') != 'complete']
done_count = len(today_habits) - len(pending)
total_count = len(today_habits)

yesterday = prev_date(1)
yesterday_dow = ((now.weekday()) % 7)
yesterday_habits = [h for h in habits if yesterday_dow in (h.get('days') or [])]
yesterday_done = sum(1 for h in yesterday_habits if yesterday in (h.get('completedDates') or []))
yesterday_pct = round(yesterday_done / len(yesterday_habits) * 100) if yesterday_habits else 0

nn_habits = [h for h in habits if h.get('isNN')]
streak = 0
for i in range(1, 60):
    check_date = prev_date(i)
    check_dow = ((now.weekday() - i) % 7)
    day_nns = [h for h in nn_habits if check_dow in (h.get('days') or [])]
    if not day_nns:
        streak += 1
        continue
    if all(check_date in (h.get('completedDates') or []) for h in day_nns):
        streak += 1
    else:
        break

today_label = now.strftime('%A, %B %-d')

msg = f"🌙 <b>Evening check-in — {today_label}</b>\n\n"
msg += f"📊 Yesterday: {yesterday_done}/{len(yesterday_habits) if yesterday_habits else 0} ({yesterday_pct}%)\n"
msg += f"🔥 Streak: {streak} day{'s' if streak != 1 else ''}\n\n"

if not pending:
    msg += "✅ <b>All habits done for today!</b> Great work."
else:
    msg += f"⏳ Still pending ({done_count}/{total_count} done):\n"
    msg += "\n".join(f"  • {h['name']}" for h in pending)
    msg += "\n\n💪 Finish strong!"

bot_token = os.environ['TELEGRAM_BOT_TOKEN']
chat_id   = os.environ['TELEGRAM_CHAT_ID']
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

data = urllib.parse.urlencode({
    'chat_id': chat_id,
    'text': msg,
    'parse_mode': 'HTML'
}).encode()

urllib.request.urlopen(urllib.request.Request(url, data=data))
print("Evening reminder sent via Telegram!")
