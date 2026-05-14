import json, urllib.request, urllib.parse, os, datetime

with open('habits.json', encoding='utf-8-sig') as f:
    habits = json.load(f)

israel = datetime.timezone(datetime.timedelta(hours=3))
now = datetime.datetime.now(israel)
js_dow = (now.weekday() + 1) % 7  # Sun=0,Mon=1,…,Sat=6

today_habits = [h for h in habits if js_dow in (h.get('days') or [])]
nn  = [h['name'] for h in today_habits if h.get('isNN')]
reg = [h['name'] for h in today_habits if not h.get('isNN') and not h.get('isBad')]
today_label = now.strftime('%A, %B %-d')

msg  = f"☀️ <b>Good morning! {today_label}</b>\n\n"
msg += "<b>Non-Negotiables:</b>\n"
msg += "\n".join(f"  ✦ {h}" for h in nn) if nn else "  (none today)"
msg += "\n\n<b>To Do Today:</b>\n"
msg += "\n".join(f"  • {h}" for h in reg) if reg else "  (none today)"
msg += "\n\n💪 Make today count!"

bot_token = os.environ['TELEGRAM_BOT_TOKEN']
chat_id   = os.environ['TELEGRAM_CHAT_ID']
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

data = urllib.parse.urlencode({
    'chat_id': chat_id,
    'text': msg,
    'parse_mode': 'HTML'
}).encode()

resp = urllib.request.urlopen(urllib.request.Request(url, data=data))
body = resp.read().decode()
print("Telegram response:", body)
print("Morning reminder sent via Telegram!")
