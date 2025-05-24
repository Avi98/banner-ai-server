from pydantic import BaseModel


class CrawlBannerResponse(BaseModel):
    """
    Response model for the banner crawling process.
    Contains the URL of the crawled banner image.
    """

    banner_url: str
    product_id: str | int
    title: str
    description: str
    product_info: dict
    category: str
    availability: str
    variants: list[dict] | None
    images: list[str]


class ProductInfoResponse(BaseModel):
    product_imgs: list[str]
    product_name: str
    product_description: str
    product_price: str
    product_category: str
    product_brand: str
    product_metadata: dict


class GetBannerPromptResponse(BaseModel):
    is_product_page: bool
    cpy_text: str
    product_industry: str
    product_template: str
    product_info: ProductInfoResponse
