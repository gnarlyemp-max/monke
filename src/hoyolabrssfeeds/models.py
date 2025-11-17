"""Model data untuk konfigurasi feed dan game."""

from enum import Enum
from pathlib import Path
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


class FeedConfig(BaseModel):
    """Konfigurasi untuk feed RSS game."""
    enabled: bool = Field(default=True, description="Aktifkan feed untuk game ini")
    title: str = Field(description="Judul feed RSS")
    description: str = Field(description="Deskripsi feed RSS")
    link: str = Field(description="Link ke halaman berita game")
    output_file: str = Field(description="Nama file output RSS")
    language: str = Field(default="id", description="Kode bahasa (id untuk Indonesia)")
    max_items: int = Field(default=20, description="Jumlah maksimal item dalam feed")
    category_filter: Optional[list[int]] = Field(
        default=None,
        description="Filter berdasarkan kategori berita (None = semua)"
    )


class NewsItem(BaseModel):
    """Item berita dari Hoyolab."""
    post_id: str
    title: str
    content: str
    created_at: int
    url: str
    cover_url: Optional[str] = None
    author: Optional[str] = None
