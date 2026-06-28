from http.server import BaseHTTPRequestHandler
import http.client, urllib.parse, json, re
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            movie = query.get('movie', ['Inception'])[0]

            # Step 1: Google search se my-subs.co URL nikalo
            search_query = urllib.parse.quote(f"site:my-subs.co {movie} subtitles")
            
            conn = http.client.HTTPSConnection("www.google.com")
            conn.request("GET", f"/search?q={search_query}&num=5", headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            res = conn.getresponse()
            html = res.read().decode('utf-8', errors='ignore')

            # my-subs.co film URL dhundo
            urls = re.findall(r'my-subs\.co/(film-versions-\d+-[^"&\s]+)', html)
            
            if not urls:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Movie nahi mili', 'results': []}).encode())
                return

            movie_path = '/' + urls[0].split('"')[0]

            # Step 2: Movie page fetch karo
            conn2 = http.client.HTTPSConnection("my-subs.co")
            conn2.request("GET", movie_path, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html',
                'Referer': 'https://my-subs.co/',
            })
            res2 = conn2.getresponse()
            page = res2.read().decode('utf-8', errors='ignore')

            # Download links nikalo
            downloads = re.findall(r'href="(https://my-subs\.co/downloads/[^"]+)"[^>]*>([^<]+)<', page)
            
            # Language sections nikalo
            lang_pattern = re.findall(r'<h3>([^<]+)</h3>.*?href="(https://my-subs\.co/downloads/[^"]+)"[^>]*>([^<]+)<', page, re.DOTALL)

            results = []
            seen = set()
            for match in re.finditer(r'### ([^\n]+)\n(.*?)(?=### |\Z)', page.replace('<h3>', '### ').replace('</h3>', '\n'), re.DOTALL):
                lang = match.group(1).strip()
                section = match.group(2)
                links = re.findall(r'href="(https://my-subs\.co/downloads/[^"]+)"[^>]*>([^<]+)<', section)
                for url, name in links[:2]:
                    if url not in seen:
                        seen.add(url)
                        results.append({'language': lang, 'name': name.strip(), 'url': url})

            # Fallback: sirf pehle 10 links
            if not results:
                for url, name in downloads[:10]:
                    results.append({'language': 'Unknown', 'name': name.strip(), 'url': url})

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'movie_page': 'https://my-subs.co' + movie_path,
                'results': results[:15]
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
