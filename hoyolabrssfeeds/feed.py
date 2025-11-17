"""Generator feed RSS untuk berita game Hoyoverse."""

import json
from datetime import datetime, timezone
from pathlib import Path
from feedgen.feed import FeedGenerator
from .models import Game, GameConfig, GlobalConfig, NewsItem
from .api import HoyolabAPIClient
from .localization import get_message


class GameFeed:
    """Generator feed untuk satu game."""
    
    def __init__(self, game: Game, game_config: GameConfig, global_config: GlobalConfig):
        self.game = game
        self.game_config = game_config
        self.global_config = global_config
        self.api_client = HoyolabAPIClient(lang=global_config.language)
    
    async def create_feeds(self) -> list[Path]:
        """
        Buat feed untuk game ini dalam semua format yang dikonfigurasi.
        
        Returns:
            List of paths ke file feed yang dibuat
        """
        print(get_message("generating_feeds", game=self.game.display_name))
        
        category_size = self.game_config.category_size or self.global_config.category_size
        
        async with self.api_client:
            news_items = await self.api_client.get_news(
                self.game,
                page_size=category_size
            )
        
        if not news_items:
            print(get_message("no_news_found", game=self.game.display_name))
            return []
        
        paths = []
        
        if self.game_config.feed.json_feed and self.game_config.feed.json_feed.path:
            json_path = await self._create_json_feed(news_items)
            paths.append(json_path)
        
        if self.game_config.feed.atom_feed and self.game_config.feed.atom_feed.path:
            atom_path = await self._create_atom_feed(news_items)
            paths.append(atom_path)
        
        return paths
    
    async def _create_json_feed(self, news_items: list[NewsItem]) -> Path:
        """Buat feed dalam format JSON."""
        json_config = self.game_config.feed.json_feed
        assert json_config is not None
        
        feed_data = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": self.game_config.title or f"{self.game.display_name} News",
            "home_page_url": f"https://www.hoyolab.com/{self.game.value}/",
            "feed_url": json_config.url or "",
            "language": self.global_config.language,
            "items": []
        }
        
        if self.game_config.icon:
            feed_data["icon"] = self.game_config.icon
        
        if self.game_config.description:
            feed_data["description"] = self.game_config.description
        
        for item in news_items:
            feed_item = {
                "id": item.url,
                "url": item.url,
                "title": item.title,
                "content_html": item.content[:500] + "..." if len(item.content) > 500 else item.content,
                "date_published": datetime.fromtimestamp(item.created_at, tz=timezone.utc).isoformat()
            }
            
            if item.cover_url:
                feed_item["image"] = item.cover_url
            
            if item.author:
                feed_item["author"] = {"name": item.author}
            
            feed_data["items"].append(feed_item)
        
        assert json_config.path is not None
        output_path = Path(json_config.path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(feed_data, f, ensure_ascii=False, indent=2)
        
        print(get_message("feed_generated", path=output_path))
        return output_path
    
    async def _create_atom_feed(self, news_items: list[NewsItem]) -> Path:
        """Buat feed dalam format Atom/RSS."""
        atom_config = self.game_config.feed.atom_feed
        assert atom_config is not None
        
        fg = FeedGenerator()
        fg.title(self.game_config.title or f"{self.game.display_name} News")
        fg.link(href=f"https://www.hoyolab.com/{self.game.value}/")
        fg.language(self.global_config.language)
        
        if atom_config.url:
            fg.id(atom_config.url)
        else:
            fg.id(f"https://www.hoyolab.com/{self.game.value}/")
        
        if self.game_config.description:
            fg.description(self.game_config.description)
        else:
            fg.description(f"News and announcements for {self.game.display_name}")
        
        if self.game_config.icon:
            fg.logo(self.game_config.icon)
        
        for item in news_items:
            fe = fg.add_entry()
            fe.id(item.url)
            fe.title(item.title)
            fe.link(href=item.url)
            fe.description(item.content[:500] + "..." if len(item.content) > 500 else item.content)
            fe.published(datetime.fromtimestamp(item.created_at, tz=timezone.utc))
            
            if item.author:
                fe.author(name=item.author)
        
        assert atom_config.path is not None
        output_path = Path(atom_config.path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fg.atom_file(str(output_path))
        
        print(get_message("feed_generated", path=output_path))
        return output_path


class GameFeedCollection:
    """Koleksi feed untuk beberapa game."""
    
    def __init__(self, feeds: list[GameFeed]):
        self.feeds = feeds
    
    @classmethod
    def from_configs(
        cls,
        game_configs: dict[Game, GameConfig],
        global_config: GlobalConfig
    ) -> "GameFeedCollection":
        """
        Buat koleksi dari dictionary konfigurasi.
        
        Args:
            game_configs: Dictionary of game configurations
            global_config: Global configuration settings
            
        Returns:
            GameFeedCollection instance
            
        Raises:
            ValueError: If no games have feed outputs configured
        """
        from .localization import get_message
        
        feeds = [
            GameFeed(game, config, global_config)
            for game, config in game_configs.items()
            if config.feed.json_feed or config.feed.atom_feed
        ]
        
        if not feeds:
            raise ValueError(get_message("no_feeds_configured"))
        
        return cls(feeds)
    
    async def create_feeds(self) -> list[Path]:
        """
        Buat semua feed.
        
        Returns:
            List of paths ke file feed yang dibuat
        """
        print(get_message("feed_collection_start"))
        
        all_paths = []
        for feed in self.feeds:
            paths = await feed.create_feeds()
            all_paths.extend(paths)
        
        print(get_message("feed_collection_complete"))
        return all_paths
