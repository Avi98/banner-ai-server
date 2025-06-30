from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any

from global_type.product_base import ProductBase


class ProductDetails(ProductBase):
    """Product information details model"""


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
