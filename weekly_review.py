import json, urllib.request, urllib.parse, os, base64, datetime

# Read current habits
with open('habits.json', encoding='utf-8-sig') as f:
    habits = json.load(f)

nn  = [h['name'] for h in habits if h.get('isNN')]
reg = [h['name'] for h in habits if not h.get('isNN')]

# Ask Groq for a review
groq_key = os.environ['GROQ_API_KEY']
prompt = f"""You are a habit coach. Review the user's current habit list and give concise, practical recommendations.

Current Non-Negotiables (highest priority daily habits):
{chr(10).join('- ' + h for h in nn) if nn else '(none)'}

Current Daily Habits (regular, can be skipped):
{chr(10).join('- ' + h for h in reg) if reg else '(none)'}

Give a short review with three sections (keep each section to 1-3 bullets, total under 200 words):

REMOVE: habits that seem redundant, vague, or low-impact
PROMOTE TO NON-NEGOTIABLE: habits that are foundational and should be daily musts
DEMOTE TO REGULAR: non-negotiables that might be too strict for daily performance

Be specific about which habit you're referring to. Use the exact habit name. If a section has no recommendations, write "None — your list looks balanced here."
"""

groq_req = urllib.request.Request(
    'https://api.groq.com/openai/v1/chat/completions',
    data=json.dumps({
        'model': 'llama-3.3-70b-versatile',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.5,
        'max_tokens': 600,
    }).encode(),
    headers={
        'Authorization': f'Bearer {groq_key}',
        'Content-Type': 'application/json',
    },
)
try:
    groq_res = json.loads(urllib.request.urlopen(groq_req).read())
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8', errors='replace')
    print(f"Groq API error: HTTP {e.code}")
    print(f"Response body: {err_body}")
    print(f"Key length: {len(groq_key) if groq_key else 0} (should be ~56)")
    print(f"Key starts with: {groq_key[:8] if groq_key else 'EMPTY'}...")
    raise
review = groq_res['choices'][0]['message']['content'].strip()

# Build WhatsApp message
today = datetime.datetime.now().strftime('%A, %B %-d')
msg = f"Weekly Habit Review — {today}\n\n{review}"

# Send via Twilio
sid   = os.environ['TWILIO_SID']
token = os.environ['TWILIO_TOKEN']
url   = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"

data = urllib.parse.urlencode({
    'From': 'whatsapp:+14155238886',
    'To':   'whatsapp:+972549715522',
    'Body': msg,
}).encode()

req = urllib.request.Request(url, data=data)
req.add_header('Authorization', 'Basic ' + base64.b64encode(f"{sid}:{token}".encode()).decode())
urllib.request.urlopen(req)
print("Weekly review sent!")
