import json, urllib.request, urllib.parse, os, datetime

with open('habits.json', encoding='utf-8-sig') as f:
    habits = json.load(f)

israel = datetime.timezone(datetime.timedelta(hours=3))
now = datetime.datetime.now(israel)
js_dow = (now.weekday() + 1) % 7  # Sun=0,Mon=1,…,Sat=6

today_habits = [h for h in habits if js_dow in (h.get('days') or [])]
gcal_habits  = [h for h in today_habits if (h.get('duration') or 0) > 0]

if not gcal_habits:
    print("No timed habits today — skipping.")
else:
    client_id     = os.environ['GOOGLE_CLIENT_ID']
    client_secret = os.environ['GOOGLE_CLIENT_SECRET']
    refresh_token = os.environ['GOOGLE_REFRESH_TOKEN']
    calendar_id   = os.environ.get('GOOGLE_CALENDAR_ID', 'primary')

    token_data = urllib.parse.urlencode({
        'client_id':     client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type':    'refresh_token',
    }).encode()
    token_req  = urllib.request.Request('https://oauth2.googleapis.com/token', data=token_data)
    token_resp = json.loads(urllib.request.urlopen(token_req).read())
    access_token = token_resp['access_token']

    created = 0
    for h in gcal_habits:
        hh, mm = map(int, h['time'].split(':'))
        start_dt = datetime.datetime(now.year, now.month, now.day, hh, mm, tzinfo=israel)
        end_dt   = start_dt + datetime.timedelta(minutes=h['duration'])
        fmt      = lambda dt: dt.strftime('%Y-%m-%dT%H:%M:%S')

        event = {
            'summary':     h['name'],
            'description': 'Vanguard habit — auto-synced',
            'start': {'dateTime': fmt(start_dt), 'timeZone': 'Asia/Jerusalem'},
            'end':   {'dateTime': fmt(end_dt),   'timeZone': 'Asia/Jerusalem'},
            'colorId': '9' if h.get('isNN') else '1',
        }

        event_data = json.dumps(event).encode()
        gcal_url   = f'https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(calendar_id)}/events'
        event_req  = urllib.request.Request(gcal_url, data=event_data)
        event_req.add_header('Authorization', f'Bearer {access_token}')
        event_req.add_header('Content-Type', 'application/json')
        urllib.request.urlopen(event_req)
        created += 1
        print(f"  Created: {h['name']} ({h['duration']} min @ {h['time']})")

    print(f"Done — {created} events created.")
