import json
from fastapi import APIRouter, Body
from config.env_variables import settings
from core.agent.llm.copy_genration_llm import JSONProcessorLLM
from core.agent.llm.image_genration_llm import BannerGenerationLLM
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

    json_processor = JSONProcessorLLM(
        endpoint_url=settings.qwen_model_endpoint,
        api_key=settings.hf_token_inference,
        temperature=0.7,
    )

    scrap_json = json.dumps({"banner": scrap})
    content = json_processor(
        prompt=scrap_json,
        max_tokens=200,
        # stop=["\n"],
    )

    content_dict = json.loads(content)
    marketing_banner = await json_processor.chain_to_text_model(
        content=content_dict,
    )

    banner_llm = BannerGenerationLLM(
        endpoint_url=settings.stable_diffusion_endpoint,
        api_key=settings.hf_token_inference,
        output_dir="generated_banners",
    )

    banner_generation = banner_llm(scrap_json)
    print(banner_generation)
    return {"message": "Banner generated successfully!"}
