# Hoyolab RSS Feeds

## Overview
Python CLI application to create RSS and JSON feeds from Hoyoverse game news (Genshin Impact, Honkai: Star Rail, Zenless Zone Zero, etc).

## Created
17 November 2025

## Project Structure
```
src/hoyolabrssfeeds/
├── __init__.py           # Main package exports
├── __main__.py           # Entry point for python -m hoyolabrssfeeds
├── cli.py                # CLI interface with Click
├── models.py             # Data models (Game, GameConfig, GlobalConfig, NewsItem)
├── api.py                # Hoyolab API client
├── feed.py               # RSS/JSON feed generator
├── config.py             # TOML configuration loader
└── localization.py       # Localized messages (configurable via TOML)
```

## Key Features
- CLI tool to create RSS and JSON feeds from Hoyolab news
- Support for 5 Hoyoverse games
- Dual feed format support: JSON Feed 1.1 and Atom/RSS
- Flexible TOML configuration with global and per-game settings
- Configurable language support (not hardcoded)
- API for programmatic usage
- Per-game customization: title, icon, description, categories, item count

## Usage

### CLI
```bash
# Generate feeds with default config
hoyolab-rss-feeds

# Specify custom config path
hoyolab-rss-feeds -c path/to/config.toml
```

### Python Module
```python
from pathlib import Path
from hoyolabrssfeeds import FeedConfigLoader, GameFeedCollection

loader = FeedConfigLoader(Path("config.toml"))
global_config = loader.get_global_config()
game_configs = loader.get_all_game_configs()
collection = GameFeedCollection.from_configs(game_configs, global_config)
await collection.create_feeds()
```

## Configuration Format
Global settings (language, category_size) + per-game settings with flexible feed formats:
```toml
language = "en-us"
category_size = 15

[genshin]
feed.json.path = "feeds/genshin.json"
feed.atom.path = "feeds/genshin.xml"
title = "Genshin Impact News"
category_size = 20
```

## Technologies
- Python 3.11+
- feedgen - Generate Atom/RSS feeds
- httpx - Async HTTP client
- click - CLI framework
- pydantic - Data validation with aliases
- tomli/tomli-w - TOML parser

## Status
Application complete and functional. Workflow actively generates both JSON and Atom feeds from Hoyolab API.
