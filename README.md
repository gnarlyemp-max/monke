# Hoyolab RSS Feeds

Generator RSS untuk berita game Hoyoverse dalam bahasa Indonesia.

## Deskripsi

Aplikasi ini membuat feed RSS dari berita resmi game Hoyoverse seperti Genshin Impact, Honkai: Star Rail, Zenless Zone Zero, dan lainnya. Semua feed, pesan, dan dokumentasi menggunakan bahasa Indonesia.

## Instalasi

```bash
pip install hoyolab-rss-feeds
```

## Penggunaan

### CLI

Anda dapat menjalankan aplikasi seperti ini:

```bash
hoyolab-rss-feeds
```

atau sebagai modul:

```bash
python -m hoyolabrssfeeds
```

Jika konfigurasi tidak ditemukan, aplikasi akan membuat konfigurasi default di direktori saat ini (`./hoyolab-rss-feeds.toml`) dan keluar. Silakan edit file konfigurasi sesuai kebutuhan Anda.

Anda dapat menentukan jalur untuk file konfigurasi dengan parameter:

```bash
hoyolab-rss-feeds -c path/ke/config.toml
```

Anda juga dapat menentukan direktori output:

```bash
hoyolab-rss-feeds -o path/ke/output
```

### Modul

Anda juga dapat membuat feed melalui kode:

```python
from pathlib import Path
from hoyolabrssfeeds import FeedConfigLoader, GameFeed, GameFeedCollection, Game

async def generate_feeds():
    loader = FeedConfigLoader(Path("path/ke/config.toml"))
    
    # semua game dalam konfigurasi
    all_configs = await loader.get_all_feed_configs()
    feed_collection = GameFeedCollection.from_configs(all_configs)
    await feed_collection.create_feeds()
    
    # hanya satu game
    genshin_config = await loader.get_feed_config(Game.GENSHIN)
    genshin_feed = GameFeed.from_config(genshin_config)
    await genshin_feed.create_feed()
```

## Konfigurasi

File konfigurasi menggunakan format TOML. Berikut contoh konfigurasi:

```toml
[genshin]
enabled = true
title = "Genshin Impact - Berita Resmi"
description = "Feed RSS untuk berita dan pengumuman Genshin Impact dari Hoyolab"
link = "https://www.hoyolab.com/genshin/"
output_file = "genshin-impact.xml"
language = "id"
max_items = 20

[starrail]
enabled = true
title = "Honkai: Star Rail - Berita Resmi"
description = "Feed RSS untuk berita dan pengumuman Honkai: Star Rail dari Hoyolab"
link = "https://www.hoyolab.com/starrail/"
output_file = "honkai-star-rail.xml"
language = "id"
max_items = 20
```

## Game yang Didukung

- Genshin Impact
- Honkai: Star Rail
- Honkai Impact 3rd
- Zenless Zone Zero
- Tears of Themis

## Lisensi

MIT
