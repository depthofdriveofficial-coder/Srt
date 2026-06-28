from http.server import BaseHTTPRequestHandler
import http.client, urllib.parse, json, os
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            movie = query.get('movie', [''])[0]
            language = query.get('lang', ['EN'])[0]
            
            api_key = os.environ.get("SUBDL_API_KEY", "")

            params = urllib.parse.urlencode({
                'api_key': api_key,
                'film_name': movie,
                'type': 'movie',
                'languages': language,
                'subs_per_page': 10
            })

            conn = http.client.HTTPSConnection("api.subdl.com")
            conn.request("GET", f"/api/v1/subtitles?{params}", headers={
                'User-Agent': 'SubtitleFinder/1.0',
                'Accept': 'application/json'
            })

            res = conn.getresponse()
            data = json.loads(res.read().decode())

            results = []
            for sub in data.get('subtitles', []):
                results.append({
                    'name': sub.get('release_name', ''),
                    'language': sub.get('language', ''),
                    'url': 'https://dl.subdl.com' + sub.get('url', '')
                })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'movie': movie,
                'results': results
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
