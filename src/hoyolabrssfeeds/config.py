"""Loader dan generator konfigurasi TOML."""

from pathlib import Path
import tomli
import tomli_w
from .models import Game, GameConfig, GlobalConfig
from .localization import get_message


DEFAULT_CONFIG = {
    "language": "en-us",
    "category_size": 15,
    "genshin": {
        "feed": {
            "json": {
                "path": "feeds/genshin.json",
                "url": "https://example.org/genshin.json"
            },
            "atom": {
                "path": "feeds/genshin.xml",
                "url": "https://example.org/genshin.xml"
            }
        },
        "categories": ["Info", "Notices"],
        "category_size": 20,
        "title": "Genshin Impact News",
        "icon": "https://example.org/genshin-icon.png"
    },
    "starrail": {
        "feed": {
            "json": {
                "path": "feeds/starrail.json",
                "url": "https://example.org/starrail.json"
            },
            "atom": {
                "path": "feeds/starrail.xml",
                "url": "https://example.org/starrail.xml"
            }
        },
        "title": "Honkai: Star Rail News"
    }
}


class FeedConfigLoader:
    """Loader untuk file konfigurasi TOML."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
    
    def create_default_config(self) -> None:
        """Buat file konfigurasi default."""
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
    
    def get_global_config(self) -> GlobalConfig:
        """
        Dapatkan konfigurasi global.
        
        Returns:
            GlobalConfig object
        """
        config = self.load_config()
        return GlobalConfig(
            language=config.get("language", "en-us"),
            category_size=config.get("category_size", 15)
        )
    
    def get_game_config(self, game: Game) -> GameConfig:
        """
        Dapatkan konfigurasi untuk game tertentu.
        
        Args:
            game: Game yang akan diambil konfigurasinya
        
        Returns:
            GameConfig object
        """
        config = self.load_config()
        game_config = config.get(game.value)
        
        if not game_config:
            raise ValueError(get_message("invalid_game", game=game.value))
        
        return GameConfig(**game_config)
    
    def get_all_game_configs(self) -> dict[Game, GameConfig]:
        """
        Dapatkan semua konfigurasi game.
        
        Returns:
            Dictionary mapping Game to GameConfig
            
        Raises:
            ValueError: If no games have feed outputs configured
        """
        config = self.load_config()
        configs = {}
        
        for game in Game:
            game_config = config.get(game.value)
            if game_config:
                game_cfg = GameConfig(**game_config)
                # Only include games with at least one feed format configured
                if game_cfg.feed.json_feed or game_cfg.feed.atom_feed:
                    configs[game] = game_cfg
        
        if not configs:
            raise ValueError(get_message("no_feeds_configured"))
        
        return configs
