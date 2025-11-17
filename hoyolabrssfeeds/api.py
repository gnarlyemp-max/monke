"""Klien API untuk mengambil berita dari Hoyolab."""

import httpx
from typing import Optional
from .models import Game, NewsItem
from .localization import get_message


class HoyolabAPIClient:
    """Klien untuk berinteraksi dengan API Hoyolab."""
    
    BASE_URL = "https://bbs-api-os.hoyolab.com/community/post/wapi"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Tutup koneksi HTTP client."""
        await self.client.aclose()
    
    async def get_news(
        self,
        game: Game,
        page_size: int = 20,
        category_id: Optional[int] = None
    ) -> list[NewsItem]:
        """
        Ambil berita dari Hoyolab untuk game tertentu.
        
        Args:
            game: Game yang akan diambil beritanya
            page_size: Jumlah item per halaman
            category_id: ID kategori berita (None untuk semua)
        
        Returns:
            List of NewsItem objects
        """
        params = {
            "gids": game.game_id,
            "page_size": page_size,
            "type": 1,
        }
        
        if category_id is not None:
            params["type"] = category_id
        
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/getNewsList",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("retcode") != 0:
                return []
            
            news_list = data.get("data", {}).get("list", [])
            
            items = []
            for post in news_list:
                post_data = post.get("post", {})
                items.append(NewsItem(
                    post_id=str(post_data.get("post_id", "")),
                    title=post_data.get("subject", ""),
                    content=post_data.get("content", ""),
                    created_at=post_data.get("created_at", 0),
                    url=f"https://www.hoyolab.com/article/{post_data.get('post_id', '')}",
                    cover_url=post_data.get("cover", ""),
                    author=post.get("user", {}).get("nickname", "Hoyolab")
                ))
            
            return items
            
        except Exception as e:
            print(get_message("api_error", error=str(e)))
            return []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
