import json
from fastapi import APIRouter, Body
from config.env_variables import settings
from core.utils.logger import Logger
from service.banner.banner_service import BannerService
from core.agent.workflow.banner_generation_workflow import BannerGenerationWorkflow
from .request_types import GenerateBannerRequest

router = APIRouter()
logger = Logger.get_logger()


@router.post("/generate_banner")
async def generate_banner(banner: GenerateBannerRequest = Body(...)):
    logger.info("Generating banner for product URL: %s", banner.productURL)

    # Scrape website data
    bannerScrap = BannerService()
    scrap = await bannerScrap.crawl_to_url(banner.productURL)
    scrap_json = json.dumps({"banner": scrap})

    # Initialize workflow
    workflow = BannerGenerationWorkflow(
        hf_token=settings.hf_token,
        model_endpoint=settings.qwen_model_endpoint,
        sd_endpoint=settings.stable_diffusion_endpoint,
    )

    # Generate banner
    result = await workflow.generate(scrap_json)
    return result
