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

msg  = f"Good morning! Plan for {today_label}\n\n"
msg += "Non-Negotiables:\n"
msg += "\n".join(f"  - {h}" for h in nn) or "  (none today)"
msg += "\n\nTo Do Today:\n"
msg += "\n".join(f"  - {h}" for h in reg) or "  (none today)"
msg += "\n\nMake today count!"

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
print("Sent!")
