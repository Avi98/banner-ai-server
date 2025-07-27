from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from pydantic import Field
from enum import Enum


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


class ProductFeatures(BaseModel):
    feature_1: Optional[str] = None
    feature_2: Optional[str] = None
    feature_3: Optional[str] = None
    feature_4: Optional[str] = None
    feature_5: Optional[str] = None


class ProductCreative(BaseModel):
    color_palette: List[str] = Field(default_factory=list)
    style: Optional[str] = None
    lighting: Optional[str] = None
    ambiance: Optional[str] = None
    cta_text: Optional[str] = None
    aspect_ratio: Optional[str] = None
    duration: Optional[str] = None


class ProductBase(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(
        alias="product_name", description="Complete product name with specifications"
    )
    sale_price: str = Field(description="Current selling price of the product")
    regular_price: str = Field(description="Original price before discount")
    offer: str = Field(description="Discount percentage or offer details")
    currency: str = Field(description="Currency code (e.g., INR, USD)")
    category: str = Field(description="Product industry category")
    description: str = Field(description="Detailed product description")
    template_type: str = Field(description="Design template style")
    ratings: Optional[str] = Field(default=None, description="Product rating out of 5")
    stock: Optional[str] = Field(description="Stock availability information")
    platform: Optional[str] = Field(default="", description="Target platform")
    feature_1: Optional[str] = Field(default=None, description="Product feature 1")
    feature_2: Optional[str] = Field(default=None, description="Product feature 2")
    feature_3: Optional[str] = Field(default=None, description="Product feature 3")
    feature_4: Optional[str] = Field(default=None, description="Product feature 4")
    feature_5: Optional[str] = Field(default=None, description="Product feature 5")
    color_palette: List[str] = Field(
        default_factory=list, description="List of color codes"
    )
    style: Optional[str] = Field(default=None, description="Design style")
    lighting: Optional[str] = Field(default=None, description="Lighting style")
    ambiance: Optional[str] = Field(default=None, description="Ambiance description")
    cta_text: Optional[str] = Field(default=None, description="Call to action text")
    aspect_ratio: Optional[str] = Field(default=None, description="Aspect ratio")
    duration: Optional[str] = Field(default=None, description="Duration")
    target_platform: Optional[str] = Field(default=None, description="Target platform")
    product_images: List[str] = Field(
        default_factory=list, description="List of product image URLs"
    )
    product_id: int = Field(default=None, description="Unique product identifier")
    sku: int = Field(default=None, description="Stock keeping unit")
    brand: Optional[str] = Field(default="", description="Brand name of the product")
    gtin: Optional[str] = Field(default="", description="Global Trade Item Number")
    mpn: Optional[str] = Field(default="", description="Manufacturer Part Number")

    # @field_validator("sale_price", "regular_price", mode="before")
    # @classmethod
    # def convert_price_to_int(cls, v):
    #     """Convert string prices to integers if needed"""
    #     if isinstance(v, str) and v.isdigit():
    #         return int(v)
    #     return v

    # @field_validator("ratings", mode="before")
    # @classmethod
    # def convert_ratings_to_float(cls, v):
    #     """Convert string ratings to float if needed"""
    #     if isinstance(v, str):
    #         try:
    #             return float(v)
    #         except ValueError:
    #             return None
    #     return v

    @field_validator("category", mode="before")
    @classmethod
    def clean_category(cls, v):
        """Clean category enum string"""
        if isinstance(v, str) and v.startswith("ProductIndustryEnum."):
            return v.replace("ProductIndustryEnum.", "")
        return v
