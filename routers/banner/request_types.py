from pydantic import BaseModel
from typing import Tuple


class GenerateBannerRequest(BaseModel):

    productURL: str


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
