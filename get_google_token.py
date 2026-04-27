"""
Run once locally to get your Google refresh token.
Usage: python get_google_token.py

In Google Cloud Console, add this to your OAuth client's Authorized Redirect URIs:
  http://localhost:8080
"""
import urllib.request, urllib.parse, json, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

CLIENT_ID     = input("Paste your Google Client ID: ").strip()
CLIENT_SECRET = input("Paste your Google Client Secret: ").strip()

REDIRECT_URI = "http://localhost:8080"
auth_code = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code['code'] = params.get('code', [''])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Authorization complete. You can close this tab.</h2>")
    def log_message(self, *args):
        pass  # silence server logs

auth_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    "&response_type=code"
    "&scope=https://www.googleapis.com/auth/calendar.events"
    "&access_type=offline"
    "&prompt=consent"
)

print("\nOpening browser for Google authorization...")
webbrowser.open(auth_url)
print("Waiting for Google to redirect back to localhost:8080...")

server = HTTPServer(('localhost', 8080), Handler)
server.handle_request()  # handles exactly one request then stops

code = auth_code.get('code', '')
if not code:
    print("No code received. Make sure http://localhost:8080 is in your OAuth redirect URIs.")
    exit(1)

data = urllib.parse.urlencode({
    'code':          code,
    'client_id':     CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri':  REDIRECT_URI,
    'grant_type':    'authorization_code',
}).encode()

req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
resp = json.loads(urllib.request.urlopen(req).read())

print("\n✓ Done! Add these 4 secrets to your GitHub repo:\n")
print(f"  GOOGLE_CLIENT_ID:     {CLIENT_ID}")
print(f"  GOOGLE_CLIENT_SECRET: {CLIENT_SECRET}")
print(f"  GOOGLE_REFRESH_TOKEN: {resp.get('refresh_token', '(missing — re-run with prompt=consent)')}")
print(f"  GOOGLE_CALENDAR_ID:   primary")
