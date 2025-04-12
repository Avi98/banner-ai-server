"""Module providing a function printing python version."""

from fastapi import APIRouter, Body
from routers.request_types import GenerateBannerRequest

router = APIRouter()


@router.post("/generate_banner")
def generate_banner(banner: GenerateBannerRequest = Body(...)):
    """Function printing python version."""
    # url = banner.productURL

    """ 
    TODO:
    1. crawl url, extract json with relevant text h2, p, title from meta,
    2. clean data and feed llm to get UI based response, remmove all product image 
    3. provide input to all products image and prompt to gernrate banner image 
    """

    return {"message": "Banner generated successfully!", "url": banner.productURL}
