from http.server import BaseHTTPRequestHandler
import http.client, urllib.parse, json, re
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            movie = query.get('movie', ['Inception'])[0]

            search_query = urllib.parse.quote(f"site:my-subs.co {movie} subtitles film-versions")
            
            conn = http.client.HTTPSConnection("www.google.com")
            conn.request("GET", f"/search?q={search_query}&num=5", headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            res = conn.getresponse()
            status = res.status
            html = res.read().decode('utf-8', errors='ignore')

            # Raw response pehle 2000 chars
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'google_status': status,
                'raw': html[:2000],
                'urls_found': re.findall(r'my-subs\.co/film-versions[^"&\s]+', html)
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
