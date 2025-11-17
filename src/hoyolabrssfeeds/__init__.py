"""Hoyolab RSS Feeds - Generator RSS untuk berita game Hoyoverse."""

from .models import Game, GameConfig, GlobalConfig, FeedFormats, FeedOutput
from .config import FeedConfigLoader
from .feed import GameFeed, GameFeedCollection

__version__ = "1.0.0"
__all__ = [
    "Game",
    "GameConfig",
    "GlobalConfig",
    "FeedFormats",
    "FeedOutput",
    "FeedConfigLoader",
    "GameFeed",
    "GameFeedCollection",
]
