from fastapi import APIRouter, Body
from sympy import product
from config.env_variables import get_settings
from core.browser.browser import Browser, BrowserConfig
from core.utils.logger import Logger
from .request_types import GenerateBannerRequest

router = APIRouter()
logger = Logger.get_logger()


@router.post("/generate_banner")
async def generate_banner(banner: GenerateBannerRequest = Body(...)):
    logger.info("Generating banner for product URL: %s", banner.productURL)

    async with Browser(config=BrowserConfig) as browser:
        await browser.navigate_with_retry(url=banner.productURL)
        if not await browser.has_content_loaded():
            logger.error("Content did not load successfully.")

            return {"error": "Content did not load successfully."}

        product_info = await browser.extract_product_info()

        if not product_info:
            logger.error("Failed to extract product information.")

            return {"error": "Failed to extract product information."}

        headers = await browser.extract_headers()
        if not headers:
            logger.error("Failed to extract headers.")

            return {"error": "Failed to extract headers."}

        metadata = await browser.extract_metadata()
        if not metadata:
            logger.error("Failed to extract metadata.")

            return {"error": "Failed to extract metadata."}

        logger.info("Metadata extracted successfully.")

        return {
            "title": metadata["title"],
            "description": metadata["description"],
            "keywords": metadata["keywords"],
            "metadata": metadata["metadata"],
            "product_info": product_info,
            "headers": headers,
        }
