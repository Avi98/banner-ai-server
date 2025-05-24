from typing import Optional, Dict, Any, Tuple
from core.agent.tools import generate_prompt_name
from core.browser.browser import Browser, BrowserConfig
from core.utils.logger import Logger
from routers.banner.request_types import GetBannerPromptRequest, GetImgPromptRequest
from routers.banner.response_types import CrawlBannerResponse
from core.agent.prompt import copy_text_prompt
from core.agent.llm import text_llm

logger = Logger.get_logger()


class BannerService:
    @staticmethod
    async def _extract_page_content(browser: Browser, url: str) -> bool:
        """Navigate to URL and verify content loading."""
        await browser.navigate_with_retry(url=url)
        if not await browser.has_content_loaded():
            logger.error("Content did not load successfully.")
            return False
        return True

    @staticmethod
    async def _extract_and_validate_data(
        browser: Browser,
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """Extract and validate all required data from the page."""
        product_info = await browser.extract_product_info()
        if not product_info:
            logger.error("Failed to extract product information.")
            return None, None, None

        headers = await browser.extract_headers()
        if not headers:
            logger.error("Failed to extract headers.")
            return None, None, None

        metadata = await browser.extract_metadata()
        if not metadata:
            logger.error("Failed to extract metadata.")
            return None, None, None

        return product_info[0], headers, metadata

    @staticmethod
    def _format_product_response(
        product: Dict[str, Any], headers: Dict[str, Any], metadata: Dict[str, Any]
    ) -> CrawlBannerResponse:
        """Format the product data into the response structure."""
        return {
            "banner_url": product.get("banner_url", ""),
            "product_id": product.get("id", 0),
            "title": product.get("title", ""),
            "description": product.get("description", ""),
            "product_info": {
                "name": product.get("name", ""),
                "brand": product.get("brand", ""),
                "price": product.get("price", ""),
                "currency": product.get("currency", ""),
                "sku": product.get("sku", ""),
                "gtin": product.get("gtin", ""),
                "mpn": product.get("mpn", ""),
                "product_url": product.get("product_url", ""),
            },
            "category": product.get("category", ""),
            "availability": product.get("availability", ""),
            "variants": product.get("variants", []),
            "images": product.get("images", []),
            "headers": headers,
            "metadata": metadata,
        }

    @staticmethod
    async def generate_banner_prompt(
        product_info: GetBannerPromptRequest,
    ) -> GetImgPromptRequest:
        """Generate banner prompt using LLM."""
        logger.info("Generating banner image prompt.")

        prompt = copy_text_prompt.format(productInfo=product_info.product_description)
        cpy_text = generate_prompt_name(text_llm, prompt)

        if not cpy_text:
            logger.error("Failed to generate marketing prompt.")
            return {"error": "Failed to generate marketing prompt."}

        logger.info(
            {
                "success": True,
                "llm_response_metadata": cpy_text.response_metadata,
            }
        )

        return {
            "marketing_prompt": cpy_text.content,
            "product_info": product_info,
        }

    @staticmethod
    async def crawl_product_page(product_url: str) -> CrawlBannerResponse:
        """Main service method to crawl product page and extract information."""
        logger.info("crawling product page.")

        async with Browser(config=BrowserConfig) as browser:
            # Step 1: Load the page
            if not await BannerService._extract_page_content(browser, product_url):
                return {"error": "Content did not load successfully."}

            # Step 2: Extract and validate all required data
            product_info, headers, metadata = (
                await BannerService._extract_and_validate_data(browser)
            )
            if not all([product_info, headers, metadata]):
                return {"error": "Failed to extract required information."}

            # Step 3: Format and return the response
            logger.info("Metadata extracted successfully.")
            return BannerService._format_product_response(
                product_info, headers, metadata
            )
