from pydantic import BaseModel
from typing import Tuple, Optional, List

from global_type.product_base import ProductBase
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
    product_metadata: dict[str, str]


class CreateOGBannerRequest(BaseModel):
    product_info: ProductBase


class CreateVedioScriptRequest(BaseModel):
    product_info: ProductBase
    aspect_ratio: str
    duration: int = EIGHT_SECONDS_MS
