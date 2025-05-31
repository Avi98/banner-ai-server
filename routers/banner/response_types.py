from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any


class ProductDetails(BaseModel):
    """Product information details model"""

    product_id: Union[int, str]
    title: str
    description: str
    name: str
    brand: str
    price: Union[int, float, str]  # Price can be numeric or string
    regular_price: Union[int, float, str]  # Regular price can be numeric or string
    offer: str
    currency: str
    sku: str
    gtin: str
    mpn: str
    product_url: str
    category: str
    availability: str
    variants: str
    images: List[str]
    product_features: str


class MetadataOgTags(BaseModel):
    """Open Graph metadata tags"""

    type: Optional[str]
    site_name: Optional[str]
    title: Optional[str]
    description: Optional[str]
    image: Optional[str]
    url: Optional[str]


class MetadataTwitterTags(BaseModel):
    """Twitter metadata tags"""

    card: Optional[str]
    site: Optional[str]
    creator: Optional[str]
    title: Optional[str]
    description: Optional[str]
    app_country: Optional[str] = None
    app_name_iphone: Optional[str] = None
    app_id_iphone: Optional[str] = None
    app_url_iphone: Optional[str] = None
    app_name_ipad: Optional[str] = None
    app_id_ipad: Optional[str] = None
    app_url_ipad: Optional[str] = None
    app_name_googleplay: Optional[str] = None
    app_id_googleplay: Optional[str] = None
    app_url_googleplay: Optional[str] = None


class MetadataInner(BaseModel):
    """Inner metadata structure"""

    description: Optional[str]
    keywords: Optional[str]
    author: Optional[str]
    canonical: Optional[str]
    og_tags: Optional[MetadataOgTags]
    twitter_tags: Optional[MetadataTwitterTags]
    schema_org: Optional[List[Any]]  # Schema.org can have various structures


class Metadata(BaseModel):
    """Complete metadata structure"""

    title: Optional[str]
    description: Optional[str] = None
    keywords: Optional[str] = None
    metadata: Optional[MetadataInner]


class CrawlBannerResponse(BaseModel):
    """
    Response model for the banner crawling process.
    Contains detailed product information and metadata.
    """

    banner_url: str
    headers: Optional[Dict[str, str]]
    metadata: Optional[Metadata]
    product_info: ProductDetails


class ProductInfoResponse(BaseModel):
    product_imgs: list[str]
    product_name: str
    product_description: str
    product_price: str
    product_category: str
    product_brand: str
    product_metadata: dict
