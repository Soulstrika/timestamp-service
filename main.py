from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime, timezone, timedelta
import os

try:
    import ntplib
    NTP_AVAILABLE = True
except ImportError:
    NTP_AVAILABLE = False

UTC_OFFSET = -3

def get_time():
    if NTP_AVAILABLE:
        try:
            client = ntplib.NTPClient()
            response = client.request("pool.ntp.org", version=3)
            utc = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
            source = "ntp"
        except:
            utc = datetime.now(tz=timezone.utc)
            source = "system"
    else:
        utc = datetime.now(tz=timezone.utc)
        source = "system"
    
    local = utc + timedelta(hours=UTC_OFFSET)
    
    return {
        "utc": utc.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "gmt-3": local.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "unix": utc.timestamp(),
        "source": source
    }

class TimestampHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = get_time()
        body = json.dumps(data, indent=2).encode()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Corriendo en puerto {port}...")
    HTTPServer(('0.0.0.0', port), TimestampHandler).serve_forever()
