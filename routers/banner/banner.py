from fastapi import APIRouter, Body
from core.utils.logger import Logger
from routers.banner.response_types import CrawlBannerResponse, GetBannerPromptResponse
from services.banner_service import BannerService
from .request_types import (
    GenerateBannerRequest,
    GetBannerPromptRequest,
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
) -> GetBannerPromptResponse:
    """Generate banner response about the product."""
    banner = BannerService()

    product_info_dump = product_info.model_dump()
    return await banner.get_product_page_info(product_info_dump)
