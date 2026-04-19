import json, urllib.request, urllib.parse, os, datetime

with open('habits.json', encoding='utf-8-sig') as f:
    habits = json.load(f)

nn  = [h['name'] for h in habits if h.get('isNN')]
reg = [h['name'] for h in habits if not h.get('isNN')]
today = datetime.datetime.now().strftime('%A, %B %-d')

msg  = f"Good morning! Plan for {today}\n\n"
msg += "Non-Negotiables:\n"
msg += "\n".join(f"  - {h}" for h in nn)
msg += "\n\nDaily Habits:\n"
msg += "\n".join(f"  - {h}" for h in reg)
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
