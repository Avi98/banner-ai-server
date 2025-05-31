from importlib import metadata
from typing import Dict, Any, Tuple, Union
from core.agent.product_agent import ProductAgent
from core.prompt.banner_image_prompt import electronics_prompts
from core.agent.product import generate_product_info
from core.utils.logger import Logger
from exceptions.invalid_product_info_error import InvalidProductInfoError
from routers.banner.request_types import Platform
from routers.banner.response_types import CrawlBannerResponse, GetBannerPromptResponse
from core.model.llm import text_llm
from services.upload_product import ProductImage
from utils.consts import EIGHT_MB

logger = Logger.get_logger("BannerService", ".services.banner_service")


TEMP_IMAGE_DIR = "./temp_product_images"
TEMP_BANNER_DIR = "./temp_product_images"

type ProductInfoType = dict[str, Any]


class BannerService:

    def __init__(self, productImg: ProductImage):
        self.product_img_client: ProductImage = productImg

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
            "product_id": product_info_dict.get("id", 0),
            "title": product_info_dict.get("title", ""),
            "description": product_info_dict.get("description", ""),
            "product_info": {
                "name": product_info_dict.get("name", ""),
                "brand": product_info_dict.get("brand", ""),
                "price": product_info_dict.get("price", ""),
                "currency": product_info_dict.get("currency", ""),
                "sku": product_info_dict.get("sku", ""),
                "gtin": product_info_dict.get("gtin", ""),
                "mpn": product_info_dict.get("mpn", ""),
                "product_url": product_info_dict.get("product_url", ""),
            },
            "category": product_info_dict.get("category", ""),
            "availability": product_info_dict.get("availability", ""),
            "variants": product_info_dict.get("variants", []),
            "images": product_info_dict.get("images", []),
            "headers": headers,
            "metadata": metadata,
        }

    @staticmethod
    async def crawl_product_page(product_url: str) -> CrawlBannerResponse:
        """Main service method to crawl product page and extract information."""

        logger.info("crawling product page.")

    async def get_product_page_info(self, product_info: dict):
        """Check if the current page metadata is a product page."""
        logger.info("Checking if the current page is a product page.")

        if not product_info or not isinstance(product_info, dict):
            logger.error("Invalid product information provided.")
            raise InvalidProductInfoError(
                "Invalid product information provided. Expected a dictionary."
            )

        has_product_info = (
            "product_name" in product_info and "product_description" in product_info
        )

        if not has_product_info:
            logger.error("Product information is incomplete.")
            raise InvalidProductInfoError(
                "Product information is incomplete. Required fields are missing."
            )

        llm_response = generate_product_info(model=text_llm, product_info=product_info)

        return {
            "product_info": product_info,
            "cpy_text": llm_response.cpy_text,
            "is_product_page": llm_response.is_product_page,
            "product_industry": llm_response.product_industry,
            "product_template": llm_response.product_template,
        }

    def _check_valid_og_banner_info(self, product_info: dict):
        """Check if the provided product information is valid for OG banner generation."""

        if not product_info or not isinstance(product_info, dict):
            logger.error("Invalid product information provided.")
            raise InvalidProductInfoError(
                "Invalid product information provided. Expected a dictionary."
            )

        if not all(
            key in product_info
            for key in ["product_name", "product_description", "product_images"]
        ):
            logger.error("Product information is incomplete.")
            raise InvalidProductInfoError(
                "Product information is incomplete. Required fields are missing."
            )
        return True

    async def create_og_banner(
        self,
        size: Tuple[int, int] = (1200, 630),
        max_size: str = EIGHT_MB,
        platform: list[Platform] = [
            Platform.FACEBOOK,
            Platform.INSTAGRAM,
            Platform.WHATSAPP,
        ],
        **product_info,
    ):
        """Generate an banner with the given product information and size for requested platforms."""

        logger.info("Creating OG banner with product information.")

        # if not self._check_valid_og_banner_info(product_info):
        #     return None

        saved_img = self.product_img_client.save_img_files(
            product_info.get("product_image"), TEMP_IMAGE_DIR
        )

        prompt_args = {
            "tagline": product_info.get("product_name"),
            "main_title_emphasis": product_info.get("product_name"),
            "sales_dates": product_info.get("product_sales", "none"),
            "discount_text": "None",
            "platform": platform,
        }
        prompt_template = electronics_prompts(**prompt_args)

        self.product_img_client.get_image_file(
            img_paths=[img_path.get("file_path") for img_path in saved_img],
            prompt=prompt_template.to_string(),
            out_dir=TEMP_BANNER_DIR,
        )
