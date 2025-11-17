# Hoyolab RSS Feeds

## Gambaran Umum
Aplikasi Python CLI untuk membuat feed RSS dari berita game Hoyoverse (Genshin Impact, Honkai: Star Rail, Zenless Zone Zero, dll) dengan antarmuka dan pesan dalam bahasa Indonesia.

## Tanggal Dibuat
17 November 2025

## Struktur Proyek
```
src/hoyolabrssfeeds/
├── __init__.py           # Ekspor utama paket
├── __main__.py           # Entry point untuk python -m hoyolabrssfeeds
├── cli.py                # Interface CLI dengan Click
├── models.py             # Model data (Game, FeedConfig, NewsItem)
├── api.py                # Klien API Hoyolab
├── feed.py               # Generator RSS feed
├── config.py             # Loader konfigurasi TOML
└── localization.py       # Teks bahasa Indonesia
```

## Fitur Utama
- CLI untuk membuat feed RSS dari berita Hoyolab
- Dukungan untuk 5 game Hoyoverse
- Semua pesan dan antarmuka dalam bahasa Indonesia
- Konfigurasi TOML yang mudah diedit
- API untuk penggunaan programatik
- Feed RSS yang dapat disesuaikan per game

## Penggunaan

### CLI
```bash
# Generate feeds dengan config default
hoyolab-rss-feeds

# Specify custom config path
hoyolab-rss-feeds -c path/to/config.toml

# Specify output directory
hoyolab-rss-feeds -o path/to/output
```

### Modul Python
```python
from pathlib import Path
from hoyolabrssfeeds import FeedConfigLoader, GameFeedCollection

loader = FeedConfigLoader(Path("config.toml"))
configs = await loader.get_all_feed_configs()
collection = GameFeedCollection.from_configs(configs)
await collection.create_feeds()
```

## Teknologi
- Python 3.11+
- feedgen - Membuat feed RSS/Atom
- httpx - HTTP client async
- click - CLI framework
- pydantic - Validasi data
- tomli/tomli-w - Parser TOML

## Status
Aplikasi lengkap dan berfungsi. Workflow aktif menghasilkan feeds dari Hoyolab API.
