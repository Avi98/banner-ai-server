from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db_session import get_db
from core.agent.product_agent import ProductAgent
from core.utils.logger import Logger
from routers.banner.response_types import CrawlBannerResponse
from services.banner_service import BannerService
from services.upload_product import ProductImage
from .request_types import (
    CrawlProductPageRequest,
    CreateOGBannerRequest,
)

router = APIRouter(prefix="/banner", tags=["Banners"])


@router.post("/crawl_product_page")
async def crawl_product_page(
    banner: CrawlProductPageRequest = Body(...), db: AsyncSession = Depends(get_db)
):
    logger = Logger.get_logger(
        __name__,
    )
    try:
        agent = ProductAgent()
        bannerService = BannerService(db)

        return await bannerService.get_product_info(banner.productURL, agent)
    except SQLAlchemyError as sqlErr:
        logger.error(f"failed to save to db: {sqlErr}")
    except Exception as e:
        raise HTTPException(status_code=500, details=str(e))


@router.post("/create_product_og_banner")
async def create_product_og_banner(
    og_banner_info: CreateOGBannerRequest, db: AsyncSession = Depends(get_db)
):
    """Generate banner response about the product."""
    logger = Logger.get_logger(
        __name__,
    )
    try:

        banner = BannerService(db)

        banner_info_dump = og_banner_info.model_dump()

        return await banner.create_og_banner(
            **banner_info_dump.get("product_info"),
        )
    except ValueError as ve:
        logger.error(f"validation error:{str(ve)}")
    except Exception as e:
        logger.error(f"error occured in create_product_og_banner:{e}")
        raise HTTPException(status_code=500, details=str(e))
