"""Generator feed RSS untuk berita game Hoyoverse."""

from datetime import datetime, timezone
from pathlib import Path
from feedgen.feed import FeedGenerator
from .models import Game, FeedConfig, NewsItem
from .api import HoyolabAPIClient
from .localization import get_message


class GameFeed:
    """Generator feed RSS untuk satu game."""
    
    def __init__(self, game: Game, config: FeedConfig):
        self.game = game
        self.config = config
        self.api_client = HoyolabAPIClient()
    
    @classmethod
    def from_config(cls, config: tuple[Game, FeedConfig]) -> "GameFeed":
        """Buat GameFeed dari tuple konfigurasi."""
        game, feed_config = config
        return cls(game, feed_config)
    
    async def create_feed(self, output_dir: Path = Path("./feeds")) -> Path:
        """
        Buat feed RSS untuk game ini.
        
        Args:
            output_dir: Direktori untuk menyimpan file RSS
        
        Returns:
            Path ke file RSS yang dibuat
        """
        print(get_message("generating_feeds", game=self.game.display_name))
        
        async with self.api_client:
            news_items = await self.api_client.get_news(
                self.game,
                page_size=self.config.max_items
            )
        
        if not news_items:
            print(get_message("no_news_found", game=self.game.display_name))
        
        fg = FeedGenerator()
        fg.title(self.config.title)
        fg.description(self.config.description)
        fg.link(href=self.config.link)
        fg.language(self.config.language)
        fg.id(self.config.link)
        
        for item in news_items:
            fe = fg.add_entry()
            fe.id(item.url)
            fe.title(item.title)
            fe.link(href=item.url)
            fe.description(self._clean_content(item.content))
            fe.published(datetime.fromtimestamp(item.created_at, tz=timezone.utc))
            
            if item.author:
                fe.author(name=item.author)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.config.output_file
        fg.rss_file(str(output_path))
        
        print(get_message("feed_generated", path=output_path))
        return output_path
    
    def _clean_content(self, content: str) -> str:
        """Bersihkan konten HTML untuk feed."""
        if len(content) > 500:
            return content[:497] + "..."
        return content


class GameFeedCollection:
    """Koleksi feed untuk beberapa game."""
    
    def __init__(self, feeds: list[GameFeed]):
        self.feeds = feeds
    
    @classmethod
    def from_configs(cls, configs: dict[Game, FeedConfig]) -> "GameFeedCollection":
        """Buat koleksi dari dictionary konfigurasi."""
        feeds = [
            GameFeed(game, config)
            for game, config in configs.items()
            if config.enabled
        ]
        return cls(feeds)
    
    async def create_feeds(self, output_dir: Path = Path("./feeds")) -> list[Path]:
        """
        Buat semua feed RSS.
        
        Args:
            output_dir: Direktori untuk menyimpan file RSS
        
        Returns:
            List of paths ke file RSS yang dibuat
        """
        print(get_message("feed_collection_start"))
        
        paths = []
        for feed in self.feeds:
            path = await feed.create_feed(output_dir)
            paths.append(path)
        
        print(get_message("feed_collection_complete"))
        return paths
