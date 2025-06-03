from io import BytesIO
from PIL import Image
from typing import Dict, Any, Tuple, Union
from core.agent.product_agent import ProductAgent

from core.model.llm import initialize_gemini_img
from core.utils.logger import Logger
from exceptions.invalid_product_info_error import InvalidProductInfoError
from routers.banner.response_types import CrawlBannerResponse
from services.upload_product import ProductImage
from services.prompt_factory import IndustryPromptFactory
from utils.consts import EIGHT_MB


TEMP_IMAGE_DIR = "./temp_product_images"
TEMP_BANNER_DIR = "./temp_product_images"

type ProductInfoType = dict[str, Any]


class BannerService:

    def __init__(self, productImg: ProductImage):
        self.logger = Logger.get_logger(
            name=__class__,
        )

    @staticmethod
    async def get_product_info(
        product_url: str, agent: ProductAgent
    ) -> CrawlBannerResponse:
        product_page, headers, metadata = await agent.crawl_product_page(product_url)

        return BannerService._format_product_response(product_page, headers, metadata)

    @staticmethod
    def _format_product_response(
        product: Union[Dict[str, Any], Tuple[ProductInfoType]],
        headers: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> CrawlBannerResponse:

        product_info_dict = None

        if isinstance(product, tuple):
            product_info_dict = {key: value for (key, value) in product}
        else:
            product_info_dict = product

        """Format the product data into the response structure."""
        return {
            "banner_url": product_info_dict.get("banner_url", ""),
            "headers": headers,
            "metadata": metadata,
            "product_info": {
                "product_id": product_info_dict.get("id", 0),
                "title": product_info_dict.get("product_name", ""),
                "description": product_info_dict.get("description", ""),
                "name": product_info_dict.get("title", ""),
                "brand": product_info_dict.get("brand", ""),
                "price": product_info_dict.get("sale_price", ""),
                "regular_price": product_info_dict.get("regular_price", ""),
                "offer": product_info_dict.get("offer", ""),
                "currency": product_info_dict.get("currency", ""),
                "sku": product_info_dict.get("id", ""),
                "gtin": product_info_dict.get("gtin", ""),
                "mpn": product_info_dict.get("mpn", ""),
                "product_url": product_info_dict.get("product_url", ""),
                "category": product_info_dict.get("category", ""),
                "availability": product_info_dict.get("availability", ""),
                "variants": product_info_dict.get("template_type", []),
                "images": product_info_dict.get("images", []),
                "product_features": product_info_dict.get("product_features", ""),
            },
        }

    def _check_valid_og_banner_info(self, product_info: dict):
        """Check if the provided product information is valid for OG banner generation."""

        if not product_info or not isinstance(product_info, dict):
            self.logger.error("Invalid product information provided.")
            raise InvalidProductInfoError(
                "Invalid product information provided. Expected a dictionary."
            )

        # if not all(
        #     key in product_info
        #     for key in ["product_name", "product_description", "product_images"]
        # ):
        #     self.logger.error("Product information is incomplete.")
        #     raise InvalidProductInfoError(
        #         "Product information is incomplete. Required fields are missing."
        #     )
        return True

    async def create_og_banner(
        self,
        size: Tuple[int, int] = (1200, 630),
        max_size: str = EIGHT_MB,
        # platform: list[Platform] = [
        #     Platform.FACEBOOK,
        #     Platform.INSTAGRAM,
        #     Platform.WHATSAPP,
        # ],
        **product_info,
    ):
        """Generate an banner with the given product information and size for requested platforms."""

        self.logger.info("Creating OG banner with product information.")

        if not self._check_valid_og_banner_info(product_info):
            return None

        ind_prompt_factory = IndustryPromptFactory(product_info)

        prompt_template = ind_prompt_factory.get_prompt(
            IndustryPromptFactory.validate_product_info(product_info)
        )

        response = initialize_gemini_img(content=prompt_template)
        return self._get_img_from(response)

    def _get_img_from(self, response):
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                image.save("gemini-native-image.png")
                image.show()
