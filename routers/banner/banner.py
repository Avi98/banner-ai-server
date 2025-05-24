from fastapi import APIRouter, Body
from core.utils.logger import Logger
from routers.banner.response_types import CrawlBannerResponse
from services.banner_service import BannerService
from .request_types import (
    GenerateBannerRequest,
    GetBannerPromptRequest,
    GetImgPromptRequest,
)

router = APIRouter()
logger = Logger.get_logger()


@router.post("/crawl_product_page")
async def crawl_product_page(
    banner: GenerateBannerRequest = Body(...),
) -> CrawlBannerResponse:
    return await BannerService.crawl_product_page(banner.productURL)


@router.post("/get_banner_prompt_data")
async def get_banner_prompt(
    product_info: GetBannerPromptRequest,
) -> GetImgPromptRequest:
    return await BannerService.generate_banner_prompt(product_info)


@router.post("/get_banner_image")
async def get_banner_image_prompt():
    logger.info("Generating banner image prompt.")
