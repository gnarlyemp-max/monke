"""Interface CLI untuk Hoyolab RSS Feeds."""

import asyncio
import sys
from pathlib import Path
import click
from .config import FeedConfigLoader
from .feed import GameFeedCollection
from .localization import get_message


@click.command()
@click.option(
    "-c",
    "--config",
    type=click.Path(path_type=Path),
    default=Path("./hoyolab-rss-feeds.toml"),
    help=get_message("help_config"),
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    default=Path("./feeds"),
    help=get_message("help_output"),
)
def main(config: Path, output: Path):
    """
    Hoyolab RSS Feeds - Generator RSS untuk berita game Hoyoverse.
    
    Aplikasi ini membuat feed RSS dari berita resmi game Hoyoverse
    seperti Genshin Impact, Honkai: Star Rail, dan lainnya.
    """
    asyncio.run(generate_feeds(config, output))


async def generate_feeds(config_path: Path, output_dir: Path):
    """Generate all RSS feeds berdasarkan konfigurasi."""
    loader = FeedConfigLoader(config_path)
    
    if not config_path.exists():
        loader.create_default_config()
        print(get_message("config_created_exit"))
        sys.exit(0)
    
    try:
        all_configs = await loader.get_all_feed_configs()
        feed_collection = GameFeedCollection.from_configs(all_configs)
        await feed_collection.create_feeds(output_dir)
    except Exception as e:
        print(get_message("error_occurred", error=str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
