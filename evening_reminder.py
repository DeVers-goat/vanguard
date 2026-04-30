import json, urllib.request, urllib.parse, os, datetime

with open('habits.json', encoding='utf-8-sig') as f:
    habits = json.load(f)

israel = datetime.timezone(datetime.timedelta(hours=3))
now = datetime.datetime.now(israel)
js_dow = (now.weekday() + 1) % 7  # Sun=0,Mon=1,...,Sat=6
today_str = now.strftime('%Y-%m-%d')

def prev_date(n=1):
    d = now - datetime.timedelta(days=n)
    return d.strftime('%Y-%m-%d')

# Today's habits scheduled for today
today_habits = [h for h in habits if js_dow in (h.get('days') or [])]
pending = [h for h in today_habits if h.get('status') != 'complete']
done_count = len(today_habits) - len(pending)
total_count = len(today_habits)

# Yesterday's score
yesterday = prev_date(1)
yesterday_dow = ((now.weekday()) % 7)  # yesterday's JS dow
yesterday_habits = [h for h in habits if yesterday_dow in (h.get('days') or [])]
yesterday_done = sum(1 for h in yesterday_habits if yesterday in (h.get('completedDates') or []))
yesterday_pct = round(yesterday_done / len(yesterday_habits) * 100) if yesterday_habits else 0

# Streak: count consecutive days where all NNs were completed
nn_habits = [h for h in habits if h.get('isNN')]
streak = 0
for i in range(1, 60):
    check_date = prev_date(i)
    check_dow = ((now.weekday() - i) % 7)
    day_nns = [h for h in nn_habits if check_dow in (h.get('days') or [])]
    if not day_nns:
        streak += 1
        continue
    all_done = all(check_date in (h.get('completedDates') or []) for h in day_nns)
    if all_done:
        streak += 1
    else:
        break

today_label = now.strftime('%A, %B %-d')

msg = f"Evening check-in — {today_label}\n\n"
msg += f"📊 Yesterday's score: {yesterday_done}/{len(yesterday_habits) if yesterday_habits else 0} ({yesterday_pct}%)\n"
msg += f"🔥 Current streak: {streak} day{'s' if streak != 1 else ''}\n\n"

if not pending:
    msg += "✅ All habits done for today! Great work.\n"
else:
    msg += f"Still pending ({done_count}/{total_count} done):\n"
    msg += "\n".join(f"  - {h['name']}" for h in pending)
    msg += "\n\nFinish strong!"

sid   = os.environ['TWILIO_SID']
token = os.environ['TWILIO_TOKEN']
url   = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"

data = urllib.parse.urlencode({
    'From': 'whatsapp:+14155238886',
    'To':   'whatsapp:+972549715522',
    'Body': msg,
}).encode()

req = urllib.request.Request(url, data=data)
req.add_header('Authorization', 'Basic ' + __import__('base64').b64encode(f"{sid}:{token}".encode()).decode())
urllib.request.urlopen(req)
print("Evening reminder sent!")
