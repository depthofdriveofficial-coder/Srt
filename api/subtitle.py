from http.server import BaseHTTPRequestHandler
import http.client, urllib.parse, json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            movie = query.get('movie', ['Inception'])[0]

            path = f"/search/query-{urllib.parse.quote(movie)}/sublanguageid-eng"
            
            # First request
            conn = http.client.HTTPSConnection("rest.opensubtitles.org")
            conn.request("GET", path, headers={
                'User-Agent': 'TemporaryUserAgent',
                'X-User-Agent': 'TemporaryUserAgent'
            })
            res = conn.getresponse()
            
            # Follow redirect if 302
            if res.status == 302:
                location = res.getheader('Location')
                parsed = urlparse(location)
                conn2 = http.client.HTTPSConnection(parsed.netloc)
                conn2.request("GET", parsed.path + ('?' + parsed.query if parsed.query else ''), headers={
                    'User-Agent': 'TemporaryUserAgent',
                    'X-User-Agent': 'TemporaryUserAgent'
                })
                res = conn2.getresponse()

            status = res.status
            raw = res.read().decode('utf-8', errors='ignore')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': status,
                'raw': raw[:1000]
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
