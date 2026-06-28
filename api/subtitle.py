from http.server import BaseHTTPRequestHandler
import urllib.request, urllib.parse, json, os
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            movie = query.get('movie', ['Inception'])[0]

            url = f"https://rest.opensubtitles.org/search/query-{urllib.parse.quote(movie)}/sublanguageid-eng"
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'TemporaryUserAgent',
                'X-User-Agent': 'TemporaryUserAgent'
            })
            
            with urllib.request.urlopen(req, timeout=8) as res:
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

