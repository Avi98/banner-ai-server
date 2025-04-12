from pydantic import BaseModel


class GenerateBannerRequest(BaseModel):
	productURL: str
