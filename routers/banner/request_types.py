from pydantic import BaseModel
from typing import Tuple, Optional, List

from core.agent.types import ProductBase
from utils.consts import EIGHT_MB, EIGHT_SECONDS_MS


class CrawlProductPageRequest(BaseModel):
    productURL: str


class GetBannerPromptRequest(BaseModel):
    product_imgs: list[str]
    product_name: str
    product_description: str
    product_price: str
    product_category: str
    product_brand: str
    product_metadata: dict


class GetImgPromptRequest(BaseModel):
    product_image: list[str]
    product_name: Optional[str] = ""
    product_title: Optional[str] = ""
    product_description: Optional[str] = ""
    banner_style: str
    banner_size: Tuple[int, int] = (500, 500)  # (width, height)
    product_metadata: dict


class CreateOGBannerRequest(BaseModel):
    size: Tuple[int, int]
    aspect_ratio: str
    max_file_size: int
    platforms: List[str]
    product_info: ProductBase


class CreateVedioScriptRequest(BaseModel):
    product_info: GetImgPromptRequest
    aspect_ratio: str
    duration: str = EIGHT_SECONDS_MS
