from typing import Any, Dict, Optional, Tuple
from core.browser.browser import Browser, BrowserConfig
from core.utils.logger import Logger


class ProductAgent:
    """Agent calls llm and browser for fetching the missing product"""

    browser: Browser = None
    logger: Logger = None
    llm: Any = None

    def __init__(self):
        self.logger = Logger.get_logger(__name__)

    async def crawl_product_page(self, product_url: str):

        async with Browser(config=BrowserConfig()) as browser:
            if not await self._extract_page_content(browser, product_url):
                return {"error": "Content did not load successfully."}

            product_info, headers, metadata = await self._extract_and_validate_data(
                browser
            )
            if not all([product_info, headers, metadata]):
                return {"error": "Failed to extract required information."}

            self.logger.info("Metadata extracted successfully.")
            return product_info, headers, metadata

    async def _extract_page_content(self, browser: Browser, url: str) -> bool:
        """Navigate to URL and verify content loading."""
        await browser.navigate_with_retry(url=url)
        if not await browser.has_content_loaded():
            self.logger.error("Content did not load successfully.")
            return False
        return True

    async def _extract_and_validate_data(
        self,
        browser: Browser,
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """Extract and validate all required data from the page."""

        product_info = await browser.extract_product_info()
        if not product_info:
            self.logger.error("Failed to extract product information.")
            return None, None, None

        headers = await browser.extract_headers()
        if not headers:
            self.logger.error("Failed to extract headers.")
            return None, None, None

        metadata = await browser.extract_metadata()
        if not metadata:
            self.logger.error("Failed to extract metadata.")
            return None, None, None

        return product_info[0], headers, metadata
