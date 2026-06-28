from http.server import BaseHTTPRequestHandler
import http.client, urllib.parse, json, re
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            movie = query.get('movie', ['Inception'])[0]

            # Search on my-subs.co
            search_path = f"/en/search-subtitle/{urllib.parse.quote(movie)}"
            
            conn = http.client.HTTPSConnection("my-subs.co")
            conn.request("GET", search_path, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://my-subs.co/',
            })
            
            res = conn.getresponse()
            status = res.status
            raw = res.read().decode('utf-8', errors='ignore')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': status,
                'raw': raw[:2000]
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
