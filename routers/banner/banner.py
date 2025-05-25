from fastapi import APIRouter, Body
from core.utils.logger import Logger
from routers.banner.response_types import CrawlBannerResponse, GetBannerPromptResponse
from services.banner_service import BannerService
from services.upload_product import ProductImage
from .request_types import (
    CrawlProductPageRequest,
    CreateOGBanner,
    GetBannerPromptRequest,
)

router = APIRouter()
logger = Logger.get_logger()


@router.post("/crawl_product_page")
async def crawl_product_page(
    banner: CrawlProductPageRequest = Body(...),
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


@router.post("/create_product_og_banner")
async def create_product_og_banner(
    og_banner_info: CreateOGBanner,
):
    product_client = ProductImage()

    """Generate banner response about the product."""
    banner = BannerService(productImg=product_client)

    product_info = og_banner_info.product_info.model_dump()
    return await banner.create_og_banner(
        size=og_banner_info.size,
        platform=og_banner_info.platforms,
        max_size=og_banner_info.max_file_size,
        aspect_ratio=og_banner_info.aspect_ratio,
        **product_info,
    )
