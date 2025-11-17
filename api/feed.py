#!/usr/bin/env python
import asyncio
import json
from http import HTTPStatus
from pathlib import Path
import sys

# Add the project root to the Python path to ensure imports work
sys.path.append(str(Path(__file__).parent.parent))

from hoyolabrssfeeds.cli import generate_feeds
from hoyolabrssfeeds.config import FeedConfigLoader

async def main(request):
    """
    Vercel serverless function to generate and serve Hoyolab RSS feeds.
    
    This function:
    1. Creates a temporary config file with output paths in /tmp
    2. Generates the RSS feeds
    3. Reads the generated feed content
    4. Returns the feed content with appropriate headers
    """
    
    # Default response headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle preflight OPTIONS request
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': HTTPStatus.NO_CONTENT,
            'headers': headers,
            'body': ''
        }
    
    # Get query parameters
    query_params = request.get('query', {})
    game = query_params.get('game', 'all')
    format_type = query_params.get('format', 'atom')
    
    # Define feed paths based on query parameters
    feeds_dir = Path('/tmp/feeds')
    feeds_dir.mkdir(exist_ok=True)
    
    if game != 'all':
        # Single game feed
        game_paths = {}
        if format_type in ['atom', 'json', 'all']:
            if format_type == 'atom':
                game_paths[f'{game}.xml'] = str(feeds_dir / f'{game}.xml')
            elif format_type == 'json':
                game_paths[f'{game}.json'] = str(feeds_dir / f'{game}.json')
            else:  # all
                game_paths[f'{game}.xml'] = str(feeds_dir / f'{game}.xml')
                game_paths[f'{game}.json'] = str(feeds_dir / f'{game}.json')
        feed_paths = {game: game_paths}
    else:
        # All games
        feed_paths = {}
        games = ['genshin', 'starrail', 'honkai', 'zenless', 'tears_of_themis']
        for g in games:
            feed_paths[g] = {}
            if format_type in ['atom', 'all']:
                feed_paths[g][f'{g}.xml'] = str(feeds_dir / f'{g}.xml')
            if format_type in ['json', 'all']:
                feed_paths[g][f'{g}.json'] = str(feeds_dir / f'{g}.json')
    
    # Create temporary config
    temp_config = {
        'language': 'en-us',
        'category_size': 15,
    }
    
    for game_name, formats in feed_paths.items():
        temp_config[game_name] = {
            'feed': {}
        }
        for format_name, path in formats.items():
            if format_name.endswith('.xml'):
                temp_config[game_name]['feed']['atom'] = {
                    'path': path,
                    'url': f'https://{request.get("headers", {}).get("host", "localhost")}/{format_name}'
                }
            elif format_name.endswith('.json'):
                temp_config[game_name]['feed']['json'] = {
                    'path': path,
                    'url': f'https://{request.get("headers", {}).get("host", "localhost")}/{format_name}'
                }
    
    # Write temporary config
    temp_config_path = Path('/tmp/hoyolab-rss-feeds.toml')
    with open(temp_config_path, 'w') as f:
        json.dump(temp_config, f)
    
    # Generate feeds
    try:
        await generate_feeds(temp_config_path)
        
        # Read the generated feed
        if game != 'all':
            if format_type == 'atom':
                feed_file = feeds_dir / f'{game}.xml'
                if feed_file.exists():
                    content_type = 'application/xml'
                    with open(feed_file, 'r') as f:
                        body = f.read()
                else:
                    return {
                        'statusCode': HTTPStatus.NOT_FOUND,
                        'headers': headers,
                        'body': json.dumps({'error': f'Atom feed for {game} not found'})
                    }
            elif format_type == 'json':
                feed_file = feeds_dir / f'{game}.json'
                if feed_file.exists():
                    content_type = 'application/json'
                    with open(feed_file, 'r') as f:
                        body = f.read()
                else:
                    return {
                        'statusCode': HTTPStatus.NOT_FOUND,
                        'headers': headers,
                        'body': json.dumps({'error': f'JSON feed for {game} not found'})
                    }
            else:
                # Return list of generated files
                generated_files = []
                for f in feeds_dir.iterdir():
                    if f.name.startswith(game):
                        generated_files.append(f.name)
                
                return {
                    'statusCode': HTTPStatus.OK,
                    'headers': {**headers, 'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'message': f'Feeds generated for {game}',
                        'files': generated_files
                    })
                }
        else:
            # Return list of all generated files
            generated_files = []
            for f in feeds_dir.iterdir():
                generated_files.append(f.name)
            
            return {
                'statusCode': HTTPStatus.OK,
                'headers': {**headers, 'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Feeds generated for all games',
                    'files': generated_files
                })
            }
        
        # Return the feed content
        return {
            'statusCode': HTTPStatus.OK,
            'headers': {**headers, 'Content-Type': content_type},
            'body': body
        }
        
    except Exception as e:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def handler(event, context):
    """Synchronous handler for Vercel serverless function."""
    # Convert Vercel event to request object
    request = {
        'method': event['httpMethod'],
        'query': event.get('queryStringParameters', {}) or {},
        'headers': event.get('headers', {}),
        'body': event.get('body', '')
    }
    
    # Run async main function
    result = asyncio.run(main(request))
    
    return result