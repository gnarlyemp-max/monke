"""Model data untuk konfigurasi feed dan game."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Game(str, Enum):
    """Enum untuk game Hoyoverse yang didukung."""
    GENSHIN = "genshin"
    STARRAIL = "starrail"
    HONKAI = "honkai"
    ZENLESS = "zenless"
    TEARS_OF_THEMIS = "tears_of_themis"

    @property
    def game_id(self) -> int:
        """ID game untuk API Hoyolab."""
        game_ids = {
            Game.GENSHIN: 2,
            Game.STARRAIL: 6,
            Game.HONKAI: 1,
            Game.ZENLESS: 8,
            Game.TEARS_OF_THEMIS: 4,
        }
        return game_ids[self]

    @property
    def display_name(self) -> str:
        """Nama tampilan game."""
        from .localization import GAME_NAMES
        return GAME_NAMES.get(self.value, self.value)


class FeedOutput(BaseModel):
    """Konfigurasi output untuk satu format feed."""
    path: Optional[str] = None
    url: Optional[str] = None


class FeedFormats(BaseModel):
    """Format feed yang tersedia (JSON dan Atom)."""
    json_feed: Optional[FeedOutput] = Field(default=None, alias="json")
    atom_feed: Optional[FeedOutput] = Field(default=None, alias="atom")
    
    class Config:
        populate_by_name = True


class GameConfig(BaseModel):
    """Konfigurasi untuk satu game."""
    feed: FeedFormats = Field(default_factory=FeedFormats)
    categories: Optional[list[str]] = None
    category_size: Optional[int] = None
    title: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class GlobalConfig(BaseModel):
    """Konfigurasi global."""
    language: str = Field(default="en-us")
    category_size: int = Field(default=15)


class NewsItem(BaseModel):
    """Item berita dari Hoyolab."""
    post_id: str
    title: str
    content: str
    created_at: int
    url: str
    cover_url: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
