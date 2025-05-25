from enum import Enum
from pydantic import BaseModel
from typing import Any, Tuple

from utils.consts import EIGHT_MB


class Platform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "INSTAGRAM"
    WHATSAPP = "WHATSAPP"


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
    product_images: list[str]
    banner_style: str
    banner_size: Tuple[int, int] = (500, 500)  # (width, height)
    product_metadata: dict


class CreateOGBanner(BaseModel):
    size: Tuple[int, int] = (1200, 630)
    aspect_ratio: str = "1.91.1"
    max_file_size: str = EIGHT_MB
    platforms: list[Platform]
    product_info: GetImgPromptRequest
