"""Main entry point for the application when run locally."""
import asyncio
import os
from pathlib import Path

# Add the project root to the Python path
import sys
sys.path.append(str(Path(__file__).parent))

from hoyolabrssfeeds.cli import generate_feeds


def main():
    """Run the feed generator with default configuration."""
    # If running locally, use the current directory for config
    config_path = Path("./hoyolab-rss-feeds.toml")
    
    # Create default config if it doesn't exist
    if not config_path.exists():
        from hoyolabrssfeeds.config import FeedConfigLoader
        loader = FeedConfigLoader(config_path)
        loader.create_default_config()
        print(f"Created default config at {config_path}")
        print("Please edit the config file and run again.")
        return
    
    # Run the async function
    asyncio.run(generate_feeds(config_path))


if __name__ == "__main__":
    main()
