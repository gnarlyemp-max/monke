# Hoyolab RSS Feeds

Generate RSS/JSON feeds for Hoyoverse game news.

## Description

This application creates RSS and JSON feeds from official Hoyoverse game news such as Genshin Impact, Honkai: Star Rail, Zenless Zone Zero, and more.

## Installation

```bash
pip install hoyolab-rss-feeds
```

## Usage

### CLI

You can run the application like this:

```bash
hoyolab-rss-feeds
```

or as module:

```bash
python -m hoyolabrssfeeds
```

If no configuration can be found, the application will create a default config in your current directory (`./hoyolab-rss-feeds.toml`) and will exit afterward.

You can specify a path for the config file with a parameter:

```bash
hoyolab-rss-feeds -c path/to/config.toml
```

### Module

It is also possible to generate the feeds via code:

```python
from pathlib import Path
from hoyolabrssfeeds import FeedConfigLoader, GameFeed, GameFeedCollection, Game

async def generate_feeds():
    loader = FeedConfigLoader(Path("path/to/config.toml"))
    
    # all games in config
    global_config = loader.get_global_config()
    all_configs = loader.get_all_game_configs()
    feed_collection = GameFeedCollection.from_configs(all_configs, global_config)
    await feed_collection.create_feeds()
    
    # only a single game
    genshin_config = loader.get_game_config(Game.GENSHIN)
    genshin_feed = GameFeed(Game.GENSHIN, genshin_config, global_config)
    await genshin_feed.create_feeds()
```

## Configuration

In the TOML config file you can define for which games you want to create a feed and in which format the feeds should be. Here is an example config:

```toml
language = "en-us"
category_size = 15

[genshin]
feed.json.path = "feeds/genshin.json"
feed.json.url = "https://example.org/genshin.json"
feed.atom.path = "feeds/genshin.xml"
feed.atom.url = "https://example.org/genshin.xml"
categories = ["Info", "Notices"]
category_size = 20
title = "Genshin Impact News"
icon = "https://example.org/genshin-icon.png"
description = "Latest news and announcements for Genshin Impact"

[starrail]
feed.json.path = "feeds/starrail.json"
feed.json.url = "https://example.org/starrail.json"
feed.atom.path = "feeds/starrail.xml"
feed.atom.url = "https://example.org/starrail.xml"
title = "Honkai: Star Rail News"
```

### Configuration Options

**Global Settings:**
- `language`: Feed language code (e.g., "en-us", "de-de", "ja-jp")
- `category_size`: Default number of items per feed (can be overridden per game)

**Per-Game Settings:**
- `feed.json.path`: Path where JSON feed should be saved
- `feed.json.url`: Public URL of the JSON feed
- `feed.atom.path`: Path where Atom/RSS feed should be saved
- `feed.atom.url`: Public URL of the Atom feed
- `categories`: Filter news by categories (optional)
- `category_size`: Override global category_size for this game (optional)
- `title`: Feed title (optional, defaults to game name)
- `icon`: Feed icon URL (optional)
- `description`: Feed description (optional)

You can configure feeds for one or both formats (JSON and Atom). Simply omit the format you don't need.

## Supported Games

- Genshin Impact (`genshin`)
- Honkai: Star Rail (`starrail`)
- Honkai Impact 3rd (`honkai`)
- Zenless Zone Zero (`zenless`)
- Tears of Themis (`tears_of_themis`)

## Feed Formats

### JSON Feed
Generates feeds following the [JSON Feed 1.1](https://www.jsonfeed.org/version/1.1/) specification.

### Atom Feed
Generates standard Atom/RSS XML feeds compatible with all feed readers.

## Vercel Deployment

You can deploy this application to Vercel to make the RSS feeds available online.

### Prerequisites
- Vercel account
- Vercel CLI installed (`npm install -g vercel`)

### Deployment Steps
1. Create a `hoyolab-rss-feeds.toml` configuration file in your project root
2. Install dependencies with `pip install -r requirements.txt`
3. Deploy with Vercel:
```bash
vercel
```
4. Follow the prompts to complete the deployment

### API Endpoints
Once deployed, you can access the feeds through these endpoints:

```
GET /api/feed?game=[game]&format=[format]
```

Where:
- `game`: Game name (`genshin`, `starrail`, `honkai`, `zenless`, `tears_of_themis`, or `all`)
- `format`: Feed format (`atom`, `json`, or `all`)

Examples:
```
GET /api/feed?game=genshin&format=atom    # Genshin Atom feed
GET /api/feed?game=starrail&format=json   # Star Rail JSON feed
GET /api/feed?game=all&format=json        # JSON feeds for all games
```

The feeds are also available directly:
- `/genshin.xml`
- `/starrail.json`
- `/honkai.xml`
- `/zenless.xml`
- `/tears_of_themis.xml`

## License

MIT
