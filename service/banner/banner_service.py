from core.scrape.scrapper import WebScraper
from .helper import is_valid_url


class BannerService:
    """Service class for handling banner-related operations."""

    def __init__(
        self,
    ):
        pass

    async def crawl_to_url(self, url: str) -> WebScraper:
        # if not is_valid_url(url):
        #     raise ValueError("Invalid URL")

        scraper = WebScraper(
            url,
            "scraped_data",
            timeout=60000,
        )
        return await scraper.scrape()
