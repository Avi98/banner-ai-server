from pydantic import BaseModel


class GenerateBannerRequest(BaseModel):
    """Request body for generating a banner."""

    productURL: str
