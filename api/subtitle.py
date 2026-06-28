from http.server import BaseHTTPRequestHandler
import http.client, urllib.parse, json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            movie = query.get('movie', ['Inception'])[0]

            path = f"/search/query-{urllib.parse.quote(movie)}/sublanguageid-eng"
            
            conn = http.client.HTTPSConnection("rest.opensubtitles.org")
            conn.request("GET", path, headers={
                'User-Agent': 'TemporaryUserAgent',
                'X-User-Agent': 'TemporaryUserAgent'
            })
            
            res = conn.getresponse()
            data = json.loads(res.read().decode())

            results = []
            for item in data[:3]:
                results.append({
                    'title': item.get('MovieName'),
                    'year': item.get('MovieYear'),
                    'language': item.get('LanguageName'),
                    'download': item.get('SubDownloadLink')
                })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'results': results, 'total': len(data)}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
