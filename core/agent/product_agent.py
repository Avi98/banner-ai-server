from typing import Any, Dict, Optional, Tuple, TypedDict, Unpack
from PIL import Image

from core.browser.browser import Browser, BrowserConfig
from core.prompt.product_info_prompt import get_product_prompt
from core.utils.logger import Logger
from core.model.llm import initialize_gemini as gemini_client
from global_type.product_base import ProductBase
from global_type.types import  PageMeta, HeadingDict

logger = Logger.get_logger(__name__, level="INFO")
class ProductInfoArg(TypedDict):
    headers: HeadingDict
    metadata: PageMeta

class ProductAgent:
    """Agent calls llm and browser for fetching the missing product"""

    def __init__(self) -> None:
        self.logger = logger

    async def crawl_product_page(self, product_url: str) -> Optional[dict[str, str]]:

        async with Browser(config=BrowserConfig()) as browser:
            if not await self._extract_page_content(browser, product_url):
                return {"error": "Content did not load successfully."}

            product_info, headers, metadata = await self._extract_and_validate_data(
                browser
            ) or ({},{},{})
            if not all([product_info, headers, metadata]):
                return {"error": "Failed to extract required information."}

            self.logger.info("Metadata extracted successfully.")

            product_image = await self._get_product_page_screenshot(browser)
            prompt = get_product_prompt()
            try:
                response = gemini_client(
                    content=[product_image, prompt], # type: ignore
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": ProductBase,
                        "responseModalities": ["TEXT"],
                    },
                )

                return self._get_product_info(
                    product_info,
                    model_json=response.text,
                    headers=headers,
                    metadata=metadata,
                )

            except Exception as e:
                self.logger.error(f"erorr occured {e}")

    def _get_product_info(
        self, product_info: Dict[str, Any], model_json: str, **product_metadata: ProductInfoArg
    ):
        model_response: Dict[str, str]

        try:
            import json

            model_response = json.loads(model_json)

            # ProductBase.model_validate(model_response)
        except Exception:
            raise Exception("Invalid llm model response for product base")

        return (
            product_info | model_response,
            product_metadata.get("headers"),
            product_metadata.get("metadata"),
        )

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
    ) -> Tuple[HeadingDict, PageMeta]:
        """Extract and validate all required data from the page."""

        product_info:list[ProductBase] = await browser.extract_product_info()

        if not product_info:
            self.logger.error("Failed to extract product information.")
            return None

        headers: HeadingDict = await browser.extract_headers()
        if not headers:
            self.logger.error("Failed to extract headers.")
            return None

        metadata: PageMeta = await browser.extract_metadata()
        if not metadata:
            self.logger.error("Failed to extract metadata.")
            return None

        return product_info[0], headers, metadata

    async def _get_product_page_screenshot(self, browser: Browser):
        """Get screenshot for the product page"""
        import base64
        from io import BytesIO

        base64_str = await browser.get_screenshot()
        image_data = base64.b64decode(base64_str)
        return Image.open(BytesIO(image_data))

    # async def _get_complete_product_info():
    #     """Get all the missing product info using screenshot passing it to reasoning llm"""

    #     gemini_clinet({"content": ''})
