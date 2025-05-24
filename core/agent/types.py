from enum import Enum
from typing import Dict
from pydantic import BaseModel, Field


class ProductIndustryEnum(str, Enum):
    FASHION = "fashion"
    ELECTRONICS = "electronics"
    HOME_DECOR = "home_decor"
    STATIONARY = "stationary"
    BEAUTY_AND_COSMETICS = "beauty_and_cosmetics"
    FOOD_AND_BEVERAGE = "food_and_beverage"


class ProductTemplateEnum(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMALIST = "minimalist"
    ELEGANT = "elegant"
    BOLD = "bold"


class ProductMetadata(BaseModel):
    product_name: str
    product_description: str
    product_price: str
    product_brand: str
    product_images: list[str]
    product_metadata: dict


class ProductInfo(BaseModel):
    product_name: str
    product_category: str
    product_industry: ProductIndustryEnum
    product_banner_prompt: str
    product_banner_template: ProductTemplateEnum
    product_theme_color: str
    product_logo: str


class ProductInfoOutput(BaseModel):
    """Product information from the llm about the product."""

    product_industry: str = Field(
        str,
        description="Industry of the product (eg. fashion, electronics, home decor, stationary, beauty_and_cosmetics, food_and_beverage)",
    )
    product_template: str = Field(
        str,
        description="Template of the product (eg. modern, classic, minimalist, elegant, bold)",
    )

    cpy_text: str = Field(str, description="Marketing prompt for banner")
