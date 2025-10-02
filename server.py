#!/usr/bin/env python3
"""
Simple HTTP server to serve RSS feed
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import logging
import json
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_env_file():
    """Load environment variables from .env file"""
    env_file = '/app/.env'
    if not os.path.exists(env_file):
        env_file = './.env'
    if os.path.exists(env_file):
        logger.info(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    logger.debug(f"Set {key}={value[:20]}...")
    else:
        logger.warning("No .env file found")

# Load .env file before doing anything else
load_env_file()

def decode_imap_utf7(s):
    """Decode IMAP modified UTF-7 string to normal UTF-8"""
    try:
        # Handle modified UTF-7 encoding used by IMAP
        # Replace & with + and &- with &
        s = s.replace('&-', '&')
        # Handle other encoded parts
        import re
        import base64
        def decode_match(match):
            encoded = match.group(1)
            try:
                # Add padding if needed
                missing_padding = len(encoded) % 4
                if missing_padding:
                    encoded += '=' * (4 - missing_padding)
                decoded_bytes = base64.b64decode(encoded, validate=True)
                return decoded_bytes.decode('utf-16-be')
            except:
                return match.group(0)  # Return original if decode fails
        
        # Replace &<base64>- patterns
        result = re.sub(r'&([A-Za-z0-9+/=]+)-', decode_match, s)
        return result
    except Exception as e:
        logger.debug(f"Failed to decode IMAP UTF-7: {s} -> {e}")
        return s  # Return original string if decode fails

class RSSHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Use local data dir if not running in Docker
        data_dir = "/app/data" if os.path.exists("/app/data") else "./data"
        super().__init__(*args, directory=data_dir, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_feeds_index()
        elif self.path == '/feed.xml' or self.path == '/feeds':
            self.serve_rss_feed('feed.xml')
        elif self.path.endswith('.xml'):
            # Serve specific mailbox feed
            feed_name = self.path[1:]  # Remove leading slash
            self.serve_rss_feed(feed_name)
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/feeds.json':
            self.serve_feeds_json()
        else:
            self.send_error(404, "Not found")
    
    def serve_feeds_index(self):
        """Serve an HTML index of available feeds"""
        try:
            # Load feeds index
            data_dir = "/app/data" if os.path.exists("/app/data") else "./data"
            index_path = os.path.join(data_dir, "feeds_index.json")
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    feeds_data = json.load(f)
            else:
                feeds_data = {'feeds': ['feed'], 'mailboxes': ['INBOX']}
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>IMAP2RSS - Feeds Disponíveis</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #333; }}
        .feed-list {{ list-style: none; padding: 0; }}
        .feed-item {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .feed-item a {{ text-decoration: none; color: #007bff; font-weight: bold; }}
        .feed-item small {{ color: #666; display: block; margin-top: 5px; }}
        .info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📰 Feeds RSS Disponíveis</h1>
        
        <div class="info">
            <strong>Modo:</strong> {feeds_data.get('feed_mode', 'combined')}<br>
            <strong>Monitored folders:</strong> {', '.join([decode_imap_utf7(mb) for mb in feeds_data.get('mailboxes', ['INBOX'])])}<br>
            <strong>Última atualização:</strong> {feeds_data.get('generated_at', 'Desconhecido')}
        </div>
        
        <h2>Feeds RSS:</h2>
        <ul class="feed-list">"""
            
            for feed in feeds_data.get('feeds', []):
                feed_url = f"http://localhost:8888/{feed}.xml"
                if feed == 'feed':
                    description = "Combined feed with all emails"
                else:
                    description = f"Emails from folder: {feed}"
                    
                html += f"""
            <li class="feed-item">
                <a href="/{feed}.xml">{feed}.xml</a>
                <small>{description}</small>
                <small><strong>URL para FreshRSS:</strong> <code>{feed_url}</code></small>
            </li>"""
            
            html += """
        </ul>
        
        <h2>APIs:</h2>
        <ul class="feed-list">
            <li class="feed-item">
                <a href="/feeds.json">feeds.json</a>
                <small>Lista de feeds em formato JSON</small>
            </li>
            <li class="feed-item">
                <a href="/health">health</a>
                <small>Status de saúde do serviço</small>
            </li>
        </ul>
    </div>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error serving feeds index: {e}")
            self.send_error(500, f"Error: {e}")
    
    def serve_rss_feed(self, feed_name):
        """Serve a specific RSS feed"""
        data_dir = "/app/data" if os.path.exists("/app/data") else "./data"
        feed_path = os.path.join(data_dir, feed_name)
        
        if not os.path.exists(feed_path):
            self.send_error(404, f"RSS feed {feed_name} not found. Check if the IMAP converter is running.")
            return
        
        try:
            with open(feed_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/rss+xml; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            logger.error(f"Error serving RSS feed {feed_name}: {e}")
            self.send_error(500, f"Error reading RSS feed: {e}")
    
    def serve_feeds_json(self):
        """Serve feeds list as JSON"""
        try:
            data_dir = "/app/data" if os.path.exists("/app/data") else "./data"
            index_path = os.path.join(data_dir, "feeds_index.json")
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    content = f.read()
            else:
                content = json.dumps({'feeds': ['feed'], 'mailboxes': ['INBOX']}).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            logger.error(f"Error serving feeds JSON: {e}")
            self.send_error(500, f"Error: {e}")
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

def run_server():
    port = int(os.getenv('HTTP_PORT', '8888'))
    server_address = ('', port)
    
    httpd = HTTPServer(server_address, RSSHandler)
    logger.info(f"Starting HTTP server on port {port}")
    logger.info(f"RSS feed will be available at http://localhost:{port}/feed.xml")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down HTTP server")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()