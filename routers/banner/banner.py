from typing import Any
from fastapi import APIRouter, Body, HTTPException
from core.agent.product_agent import ProductAgent
from core.model.llm import initialize_gemini
from core.utils.logger import Logger
from routers.banner.response_types import CrawlBannerResponse
from services.banner_service import BannerService
from services.upload_product import ProductImage
from .request_types import (
    CrawlProductPageRequest,
    CreateOGBannerRequest,
    CreateVedioScriptRequest,
)

router = APIRouter()


@router.get("/test-llm")
def test():
    # llm = initialize_imagen()
    llm = initialize_gemini()
    # model: Any = llm.invoke("can A dog reading a newspaper")
    return llm


# step 1
@router.post("/crawl_product_page")
async def crawl_product_page(
    banner: CrawlProductPageRequest = Body(...),
):

    agent = ProductAgent()
    return await BannerService.get_product_info(banner.productURL, agent)


@router.post("/create_product_og_banner")
async def create_product_og_banner(
    og_banner_info: CreateOGBannerRequest,
):
    """Generate banner response about the product."""
    logger = Logger.get_logger(
        __name__,
    )
    try:

        product_client = ProductImage()

        banner = BannerService(productImg=product_client)

        banner_info_dump = og_banner_info.model_dump()

        return await banner.create_og_banner(
            size=og_banner_info.size,
            platform=og_banner_info.platforms,
            max_size=og_banner_info.max_file_size,
            aspect_ratio=og_banner_info.aspect_ratio,
            **banner_info_dump.get("product_info"),
        )
    except ValueError as ve:
        logger.error(f"validation error:{str(ve)}")
    except Exception as e:
        logger.error(f"error occured in create_product_og_banner:{e}")
        raise HTTPException(status_code=500, details=str(e))


@router.post("generate_vedio_script")
async def create_vedio_script(vedio_script_req: CreateVedioScriptRequest):
    """Create a vedio script for the product"""

    pass
