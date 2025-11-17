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
def main(config: Path):
    """
    Hoyolab RSS Feeds - Generate RSS/JSON feeds for Hoyoverse games.
    
    Creates feeds from official Hoyoverse game news like
    Genshin Impact, Honkai: Star Rail, and more.
    """
    asyncio.run(generate_feeds(config))


async def generate_feeds(config_path: Path):
    """Generate all feeds based on configuration."""
    loader = FeedConfigLoader(config_path)
    
    if not config_path.exists():
        loader.create_default_config()
        print(get_message("config_created_exit"))
        sys.exit(0)
    
    try:
        global_config = loader.get_global_config()
        game_configs = loader.get_all_game_configs()
        feed_collection = GameFeedCollection.from_configs(game_configs, global_config)
        await feed_collection.create_feeds()
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(get_message("error_occurred", error=str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
