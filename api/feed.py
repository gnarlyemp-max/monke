import asyncio
import json
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path
import sys
from urllib.parse import urlparse, parse_qs


from hoyolabrssfeeds.cli import generate_feeds
from hoyolabrssfeeds.config import FeedConfigLoader

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        game = query_params.get('game', ['all'])[0]
        format_type = query_params.get('format', ['atom'])[0]

        feeds_dir = Path('/tmp/feeds')
        feeds_dir.mkdir(exist_ok=True)

        temp_config = {
            'language': 'en-us',
            'category_size': 15,
        }

        host = self.headers.get('host', 'localhost')

        if game != 'all':
            if format_type in ['atom', 'json', 'all']:
                temp_config[game] = {'feed': {}}
                if format_type == 'atom' or format_type == 'all':
                    temp_config[game]['feed']['atom'] = {
                        'path': str(feeds_dir / f'{game}.xml'),
                        'url': f'https://{host}/{game}.xml'
                    }
                if format_type == 'json' or format_type == 'all':
                    temp_config[game]['feed']['json'] = {
                        'path': str(feeds_dir / f'{game}.json'),
                        'url': f'https://{host}/{game}.json'
                    }
        else:
            games = ['genshin', 'starrail', 'honkai', 'zenless', 'tears_of_themis']
            for g in games:
                temp_config[g] = {'feed': {}}
                if format_type in ['atom', 'all']:
                    temp_config[g]['feed']['atom'] = {
                        'path': str(feeds_dir / f'{g}.xml'),
                        'url': f'https://{host}/{g}.xml'
                    }
                if format_type in ['json', 'all']:
                    temp_config[g]['feed']['json'] = {
                        'path': str(feeds_dir / f'{g}.json'),
                        'url': f'https://{host}/{g}.json'
                    }

        temp_config_path = Path('/tmp/hoyolab-rss-feeds.toml')
        with open(temp_config_path, 'w') as f:
            # Use tomli_w to write the config
            import tomli_w
            tomli_w.dump(temp_config, f)

        try:
            asyncio.run(generate_feeds(temp_config_path))

            if game != 'all' and format_type in ['atom', 'json']:
                if format_type == 'atom':
                    feed_file = feeds_dir / f'{game}.xml'
                    content_type = 'application/xml'
                else:
                    feed_file = feeds_dir / f'{game}.json'
                    content_type = 'application/json'
                
                if feed_file.exists():
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    with open(feed_file, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Feed not found'}).encode('utf-8'))
            else:
                generated_files = [f.name for f in feeds_dir.iterdir() if f.is_file()]
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'message': 'Feeds generated successfully',
                    'files': generated_files
                }).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        
        return
