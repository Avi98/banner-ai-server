from typing import Optional, Dict, Any, Tuple
from core.agent.product import generate_product_info
from core.browser.browser import Browser, BrowserConfig
from core.utils.logger import Logger
from exceptions.invalid_product_info_error import InvalidProductInfoError
from routers.banner.request_types import Platform
from routers.banner.response_types import CrawlBannerResponse, GetBannerPromptResponse
from core.agent.llm import text_llm
from utils.consts import EIGHT_MB

logger = Logger.get_logger("BannerService", ".services.banner_service")


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
    async def crawl_product_page(product_url: str) -> CrawlBannerResponse:
        """Main service method to crawl product page and extract information."""
        logger.info("crawling product page.")

        async with Browser(config=BrowserConfig) as browser:
            if not await BannerService._extract_page_content(browser, product_url):
                return {"error": "Content did not load successfully."}

            product_info, headers, metadata = (
                await BannerService._extract_and_validate_data(browser)
            )
            if not all([product_info, headers, metadata]):
                return {"error": "Failed to extract required information."}

            logger.info("Metadata extracted successfully.")
            return BannerService._format_product_response(
                product_info, headers, metadata
            )

    async def get_product_page_info(self, product_info: dict):
        """Check if the current page metadata is a product page."""
        logger.info("Checking if the current page is a product page.")

        if not product_info or not isinstance(product_info, dict):
            logger.error("Invalid product information provided.")
            raise InvalidProductInfoError(
                "Invalid product information provided. Expected a dictionary."
            )

        has_product_info = (
            "product_name" in product_info and "product_description" in product_info
        )

        if not has_product_info:
            logger.error("Product information is incomplete.")
            raise InvalidProductInfoError(
                "Product information is incomplete. Required fields are missing."
            )

        llm_response = generate_product_info(model=text_llm, product_info=product_info)

        return {
            "product_info": product_info,
            "cpy_text": llm_response.cpy_text,
            "is_product_page": llm_response.is_product_page,
            "product_industry": llm_response.product_industry,
            "product_template": llm_response.product_template,
        }

    async def create_og_banner(
        self,
        size: Tuple[int, int] = (1200, 630),
        max_size: str = EIGHT_MB,
        platform: list[Platform] = [
            Platform.FACEBOOK,
            Platform.INSTAGRAM,
            Platform.WHATSAPP,
        ],
        **product_info,
    ):
        """Generate an banner with the given product information and size for requested platforms."""
        logger.info("Creating OG banner with product information.")

        if not product_info or not isinstance(product_info, dict):
            logger.error("Invalid product information provided.")
            raise InvalidProductInfoError(
                "Invalid product information provided. Expected a dictionary."
            )

        if not all(
            key in product_info
            for key in ["product_name", "product_description", "product_imgs"]
        ):
            logger.error("Product information is incomplete.")
            raise InvalidProductInfoError(
                "Product information is incomplete. Required fields are missing."
            )
