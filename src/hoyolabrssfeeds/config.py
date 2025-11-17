"""Loader dan generator konfigurasi TOML."""

from pathlib import Path
from typing import Optional
import tomli
import tomli_w
from .models import Game, FeedConfig
from .localization import get_message


DEFAULT_CONFIG = {
    "genshin": {
        "enabled": True,
        "title": "Genshin Impact - Berita Resmi",
        "description": "Feed RSS untuk berita dan pengumuman Genshin Impact dari Hoyolab",
        "link": "https://www.hoyolab.com/genshin/",
        "output_file": "genshin-impact.xml",
        "language": "id",
        "max_items": 20,
    },
    "starrail": {
        "enabled": True,
        "title": "Honkai: Star Rail - Berita Resmi",
        "description": "Feed RSS untuk berita dan pengumuman Honkai: Star Rail dari Hoyolab",
        "link": "https://www.hoyolab.com/starrail/",
        "output_file": "honkai-star-rail.xml",
        "language": "id",
        "max_items": 20,
    },
    "honkai": {
        "enabled": False,
        "title": "Honkai Impact 3rd - Berita Resmi",
        "description": "Feed RSS untuk berita dan pengumuman Honkai Impact 3rd dari Hoyolab",
        "link": "https://www.hoyolab.com/honkai/",
        "output_file": "honkai-impact-3rd.xml",
        "language": "id",
        "max_items": 20,
    },
    "zenless": {
        "enabled": True,
        "title": "Zenless Zone Zero - Berita Resmi",
        "description": "Feed RSS untuk berita dan pengumuman Zenless Zone Zero dari Hoyolab",
        "link": "https://www.hoyolab.com/zenless/",
        "output_file": "zenless-zone-zero.xml",
        "language": "id",
        "max_items": 20,
    },
    "tears_of_themis": {
        "enabled": False,
        "title": "Tears of Themis - Berita Resmi",
        "description": "Feed RSS untuk berita dan pengumuman Tears of Themis dari Hoyolab",
        "link": "https://www.hoyolab.com/tot/",
        "output_file": "tears-of-themis.xml",
        "language": "id",
        "max_items": 20,
    },
}


class FeedConfigLoader:
    """Loader untuk file konfigurasi TOML."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
    
    def create_default_config(self) -> None:
        """Buat file konfigurasi default."""
        config_content = "# Konfigurasi Hoyolab RSS Feeds\n"
        config_content += "# Edit file ini untuk menyesuaikan feed RSS Anda\n\n"
        
        with open(self.config_path, "wb") as f:
            tomli_w.dump(DEFAULT_CONFIG, f)
        
        print(get_message("config_created", path=self.config_path))
    
    def load_config(self) -> dict:
        """Muat konfigurasi dari file TOML."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                get_message("config_not_found", path=self.config_path)
            )
        
        with open(self.config_path, "rb") as f:
            return tomli.load(f)
    
    async def get_feed_config(self, game: Game) -> tuple[Game, FeedConfig]:
        """
        Dapatkan konfigurasi feed untuk game tertentu.
        
        Args:
            game: Game yang akan diambil konfigurasinya
        
        Returns:
            Tuple of (Game, FeedConfig)
        """
        config = self.load_config()
        game_config = config.get(game.value)
        
        if not game_config:
            raise ValueError(get_message("invalid_game", game=game.value))
        
        return (game, FeedConfig(**game_config))
    
    async def get_all_feed_configs(self) -> dict[Game, FeedConfig]:
        """
        Dapatkan semua konfigurasi feed.
        
        Returns:
            Dictionary mapping Game to FeedConfig
        """
        config = self.load_config()
        configs = {}
        
        for game in Game:
            game_config = config.get(game.value)
            if game_config:
                configs[game] = FeedConfig(**game_config)
        
        return configs
