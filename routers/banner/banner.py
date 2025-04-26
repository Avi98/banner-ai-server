from fastapi import APIRouter, Body
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
        }
