from enum import Enum
from typing import Dict, Union
from openai import BaseModel
from pydantic import Field


class ProductIndustryEnum(str, Enum):
    FASHION = "fashion"
    ELECTRONICS = "electronics"
    HOME_DECOR = "home_decor"
    STATIONARY = "stationary"
    BEAUTY_AND_COSMETICS = "beauty_and_cosmetics"
    FOOD_AND_BEVERAGE = "food_and_beverage"


class Platform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "INSTAGRAM"
    WHATSAPP = "WHATSAPP"


class ProductTemplateEnum(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMALIST = "minimalist"
    ELEGANT = "elegant"
    BOLD = "bold"


class Stock(BaseModel):
    items: int
    out_of_stock: bool
    not_found: bool


class ProductBase(BaseModel):
    sale_price: int
    regular_price: int
    offer: str
    currency: str
    category: ProductIndustryEnum
    description: str
    product_features: str
    template_type: ProductTemplateEnum
    stock: Stock
    platforms: list[Platform]
    product_images: list[str]
    product_id: str
    name: str
    brand: str = ""
    sku: str
    gtin: str = ""
    mpn: str = ""
    product_metadata: Dict = Field(default_factory=dict)
