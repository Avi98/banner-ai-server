from fastapi import APIRouter, Body
from core.utils.logger import Logger
from service.banner.banner_service import BannerService
from .request_types import GenerateBannerRequest

router = APIRouter()

logger = Logger.get_logger()


@router.post("/generate_banner")
async def generate_banner(banner: GenerateBannerRequest = Body(...)):
    logger.info("Generating banner for product URL: %s", banner.productURL)
    bannerScrap = BannerService()
    scrap = await bannerScrap.crawl_to_url(banner.productURL)
    print(scrap)

    return {"message": "Banner generated successfully!", "banner": scrap}
