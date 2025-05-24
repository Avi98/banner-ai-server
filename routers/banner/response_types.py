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


class GetBannerPromptResponse(BaseModel):
    is_product_page: bool
    marketing_prompt: str
    product_info: CrawlBannerResponse
