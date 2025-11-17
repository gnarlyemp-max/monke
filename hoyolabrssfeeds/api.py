"""Web scraper for fetching news from the official Hoyoverse news pages."""

import httpx
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from .models import Game, NewsItem
from .localization import get_message

class HoyolabNewsScraper:
    """Scraper for the official Hoyoverse news websites."""

    BASE_URLS = {
        Game.GENSHIN: "https://genshin.hoyoverse.com/{lang}/news",
        Game.STARRAIL: "https://hsr.hoyoverse.com/{lang}/news",
        Game.HONKAI: "https://honkaiimpact3.hoyoverse.com/{lang}/news",
        Game.ZENLESS: "https://zenless.hoyoverse.com/{lang}/news",
        Game.TEARS_OF_THEMIS: "https://tot.hoyoverse.com/{lang}/news",
    }

    def __init__(self, lang: str = "en-us"):
        self.lang = lang
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()

    async def get_news(
        self,
        game: Game,
        page_size: int = 20
    ) -> list[NewsItem]:
        """
        Fetch news from the official website for a specific game.
        
        Args:
            game: The game to fetch news for
            page_size: The number of items per page
        
        Returns:
            A list of NewsItem objects
        """
        url = self.BASE_URL[game].format(lang=self.lang)
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            news_list = soup.select(".news-item")
            
            items = []
            for item in news_list[:page_size]:
                title_element = item.select_one(".news-title")
                time_element = item.select_one(".news-time")
                link_element = item.select_one("a")
                
                if title_element and time_element and link_element:
                    title = title_element.text.strip()
                    
                    # The date is in MM/DD/YYYY format, convert to timestamp
                    date_str = time_element.text.strip()
                    created_at = int(datetime.strptime(date_str, "%m/%d/%Y").replace(tzinfo=timezone.utc).timestamp())
                    
                    article_url = link_element["href"]
                    if not article_url.startswith("http"):
                        base_url = self.BASE_URL[game].split("/news")[0].format(lang=self.lang)
                        article_url = f"{base_url}{article_url}"

                    items.append(NewsItem(
                        post_id=article_url.split("/")[-1],
                        title=title,
                        content="",  # Content is not available on the list page
                        created_at=created_at,
                        url=article_url,
                        author=game.display_name
                    ))
            
            return items
            
        except Exception as e:
            print(get_message("api_error", error=str(e)))
            return []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
