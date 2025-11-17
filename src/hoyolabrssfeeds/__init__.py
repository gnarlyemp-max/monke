"""Hoyolab RSS Feeds - Generator RSS untuk berita game Hoyoverse dalam bahasa Indonesia."""

from .models import Game, FeedConfig
from .config import FeedConfigLoader
from .feed import GameFeed, GameFeedCollection

__version__ = "1.0.0"
__all__ = [
    "Game",
    "FeedConfig",
    "FeedConfigLoader",
    "GameFeed",
    "GameFeedCollection",
]
