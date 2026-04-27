import json, urllib.request, urllib.parse, os, datetime

# ── Load habits ──────────────────────────────────────────────────────────────
with open('habits.json', encoding='utf-8-sig') as f:
    habits = json.load(f)

# Always use Israel time (UTC+3) regardless of server timezone
israel = datetime.timezone(datetime.timedelta(hours=3))
now = datetime.datetime.now(israel)

# Python weekday(): Mon=0…Sun=6 → JS getDay(): Sun=0,Mon=1,…,Sat=6
js_dow = (now.weekday() + 1) % 7

today_habits = [h for h in habits if js_dow in (h.get('days') or [])]
nn  = [h['name'] for h in today_habits if h.get('isNN')]
reg = [h['name'] for h in today_habits if not h.get('isNN') and not h.get('isBad')]
today_label = now.strftime('%A, %B %-d')

# ── WhatsApp message ─────────────────────────────────────────────────────────
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
print("WhatsApp sent!")

# ── Google Calendar sync ─────────────────────────────────────────────────────
gcal_habits = [h for h in today_habits if (h.get('duration') or 0) > 0]

if not gcal_habits:
    print("No timed habits today — skipping Calendar sync.")
else:
    client_id     = os.environ.get('GOOGLE_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN', '')
    calendar_id   = os.environ.get('GOOGLE_CALENDAR_ID', 'primary')

    if not all([client_id, client_secret, refresh_token]):
        print("Google credentials not set — skipping Calendar sync.")
    else:
        # Get access token
        token_data = urllib.parse.urlencode({
            'client_id':     client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type':    'refresh_token',
        }).encode()
        token_req = urllib.request.Request('https://oauth2.googleapis.com/token', data=token_data)
        token_resp = json.loads(urllib.request.urlopen(token_req).read())
        access_token = token_resp['access_token']

        created = 0

        for h in gcal_habits:
            hh, mm = map(int, h['time'].split(':'))
            start_dt = datetime.datetime(
                now.year, now.month, now.day, hh, mm,
                tzinfo=israel
            )
            end_dt = start_dt + datetime.timedelta(minutes=h['duration'])
            fmt = lambda dt: dt.strftime('%Y-%m-%dT%H:%M:%S')

            event = {
                'summary': h['name'],
                'description': 'Vanguard habit — auto-synced',
                'start': {'dateTime': fmt(start_dt), 'timeZone': 'Asia/Jerusalem'},
                'end':   {'dateTime': fmt(end_dt),   'timeZone': 'Asia/Jerusalem'},
                'colorId': '9' if h.get('isNN') else '1',  # blueberry for NN, lavender for regular
            }

            event_data = json.dumps(event).encode()
            gcal_url = f'https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(calendar_id)}/events'
            event_req = urllib.request.Request(gcal_url, data=event_data)
            event_req.add_header('Authorization', f'Bearer {access_token}')
            event_req.add_header('Content-Type', 'application/json')
            urllib.request.urlopen(event_req)
            created += 1
            print(f"  Created: {h['name']} ({h['duration']} min @ {h['time']})")

        print(f"Calendar sync done — {created} events created.")
