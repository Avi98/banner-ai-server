import asyncio
import random
from io import BytesIO
from types import CoroutineType
from PIL import Image
from typing import Dict, Any, List, Tuple, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry

from core.agent.product_agent import ProductAgent
from core.model.llm import initialize_gemini_img
from core.utils.logger import Logger
from exceptions.invalid_product_info_error import InvalidProductInfoError
from models.banner_var_model import BannerVariant, Product
from services.banner_variant_service import BannerVariantService
from services.prompt_factory import IndustryPromptFactory
from services.s3_service import S3Service
from utils.type_cast import str_to_float


TEMP_IMAGE_DIR = "./temp_product_images"
TEMP_BANNER_DIR = "./temp_product_images"

type ProductInfoType = dict[str, Any]

T = TypeVar("T", bound=S3Service)


class BannerService:

    s3_factory: T = None

    def __init__(
        self, db: AsyncSession, s3_fact: T, variation_service: BannerVariantService
    ):
        self.logger = Logger.get_logger(
            name=__class__,
        )
        self.db = db
        self.s3_factory = s3_fact
        self.var_service = variation_service

    async def get_product_info(self, product_url: str, agent: ProductAgent):
        product_info, headers, metadata = await agent.crawl_product_page(product_url)
        product = await self._save_product(product_info)
        return BannerService._format_product_response(
            product={**product_info | {"id": product.id}},
            headers=headers,
            metadata=metadata,
        )

    @staticmethod
    def _format_product_response(
        product: Union[Dict[str, Any], Tuple[ProductInfoType]],
        headers: Dict[str, Any],
        metadata: Dict[str, Any],
    ):

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
                "name": product_info_dict.get("name", ""),
                "brand": product_info_dict.get("brand", ""),
                "price": product_info_dict.get("sale_price", ""),
                "regular_price": product_info_dict.get("regular_price", ""),
                "description": product_info_dict.get("description"),
                "offer": product_info_dict.get("offer", ""),
                "currency": product_info_dict.get("currency", ""),
                "sku": product_info_dict.get("id", ""),
                "gtin": product_info_dict.get("gtin", ""),
                "mpn": product_info_dict.get("mpn", ""),
                "stock": product_info_dict.get("stock", ""),
                "ratings": product_info_dict.get("ratings", ""),
                "platform": product_info_dict.get("platform", ""),
                "feature_1": product_info_dict.get("feature_1", ""),
                "feature_2": product_info_dict.get("feature_2", ""),
                "feature_3": product_info_dict.get("feature_3", ""),
                "feature_4": product_info_dict.get("feature_4", ""),
                "feature_5": product_info_dict.get("feature_5", ""),
                "color_palette": product_info_dict.get("color_palette", ""),
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
        **product_info,
    ):
        """Generate an banner with the given product information and size for requested platforms."""

        self.logger.info("Creating OG banner with product information.")

        if not self._check_valid_og_banner_info(product_info):
            return None

        ind_prompt_factory = IndustryPromptFactory(product_info)

        prompt_template = ind_prompt_factory.get_prompt(
            # IndustryPromptFactory.validate_pr product_info(product_info)
            product_info
        )

        response = initialize_gemini_img(content=prompt_template)

        img_bytes = self._get_img_from(response, in_mem=True)
        banners_urls = await self._create_upload_variants(
            img_bytes, 3, product_name=product_info.get("product_name", "")
        )

        # save to DB
        for i, s3_url in enumerate(banners_urls):
            await self._save_banner_link(
                s3_url,
                product_id=product_info.get("product_id"),
                variant_num=i,
                db_session=self.db,
            )

        return banners_urls

        # await self._save_banner_link(
        #     s3_url, product_id=product_info.get("product_id"), variant_num=1
        # )

    async def _generate_variant(self, base_img: bytes, num_var: int) -> List[bytes]:
        """
        Creates multi variant for provided img
        Args:
            base_img: bytes for img
            num_var: number of variant to be generated

        Returns:
            list of bytes
        """

        variant = self.var_service.generate_variants(base_img, num_variant=num_var)

        return await asyncio.gather(*variant, return_exceptions=True)

    async def _create_upload_variants(
        self, base_img: bytes, n: int, product_name: str
    ) -> List[CoroutineType]:
        """
        Uploads bytes to S3
        Args:
            bytes: img bytes
            n: number of variants
        Returns:
            list of urls
        """

        variants = await self._generate_variant(base_img=base_img, num_var=n)
        s3 = self.s3_factory()
        s3_urls = [
            s3.upload_byte(byte, name=f"{product_name}_{i}")
            for i, byte in enumerate(variants)
        ]

        return await asyncio.gather(*s3_urls)

    # def _generate_variations(self, banner: bytes, num_var: int):
    #     """
    #     Generate variations based on the img.
    #     Upload the variations on S3 & get the link for the variation link
    #     Save links in DB for their respective product_id
    #     """

    #     banner_bytes = self.var_service.generate_variants(banner, num_variant=num_var)
    #     return banner_bytes

    async def _save_product(self, product_info: Dict[str, Any]) -> Product:
        """
        Save product details to database
        Args:
            product_info: Dictionary containing product information
        Returns:
            Product: Saved product instance
        """
        try:
            price = str_to_float(product_info.get("sale_price", "0"))
            regular_price = str_to_float(product_info.get("regular_price", "0"))
            ratings = str_to_float(product_info.get("ratings", "0"))

            product = Product(
                # uuid=product_info.get("product_id"),
                title=product_info.get("title", ""),
                description=product_info.get("description", ""),
                price=price,
                regular_price=regular_price,
                currency=product_info.get("currency", ""),
                offer=product_info.get("offer", ""),
                brand=product_info.get("brand", ""),
                category=product_info.get("category", ""),
                stock=product_info.get("stock", "inventory_not_found"),
                ratings=ratings,
                image_url=(
                    product_info.get("images", [""])[0]
                    if len(product_info.get("images", [""])) > 1
                    else ""
                ),
                product_url=product_info.get("product_url", ""),
                feature_1=product_info.get("feature_1", ""),
                feature_2=product_info.get("feature_2", ""),
                feature_3=product_info.get("feature_3", ""),
                feature_4=product_info.get("feature_4", ""),
                feature_5=product_info.get("feature_5", ""),
                is_live=True,
            )

            self.db.add(product)

            await self.db.commit()

            await self.db.refresh(product)

            self.logger.info(f"Successfully saved product with ID: {product.id}")
            return product

        except SQLAlchemyError as e:
            await self.db.rollback()
            self.logger.error(f"Database error while saving product: {str(e)}")
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Unexpected error while saving product: {str(e)}")
            raise

    def _get_img_from(self, response, in_mem=True):
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                if in_mem:
                    import io

                    in_mem_file = io.BytesIO()
                    image.save(in_mem_file, format="png")
                    return in_mem_file.getvalue()

                elif not in_mem:
                    image.save("gemini-native-image.png")
                    image.show()

    async def _save_banner_link(
        self, s3_url: str, product_id: int, variant_num: int, db_session
    ) -> BannerVariant:
        """Save banner variant s3 url to db"""

        try:
            save_s3_url: str = s3_url
            s3_key = save_s3_url.split(".amazonaws.com/")[-1] if save_s3_url else None
            product_id = int(product_id)

            product = await db_session.get(Product, product_id)

            banner_variant = BannerVariant(
                variant_number=variant_num,
                s3_url=save_s3_url,
                s3_key=s3_key,
                status="completed",  # Set initial status as completed since we have the URL
                generation_time=0.0,  # You can update this if you track generation time
                view_count=0,
                is_selected=False,
                is_downloaded=False,
            )

            banner_variant.product = product
            db_session.add(banner_variant)
            await db_session.commit()
            await db_session.refresh(banner_variant)

            self.logger.info(
                f"Successfully saved banner variant with ID: {banner_variant.id}"
            )
            return banner_variant

        except SQLAlchemyError as e:
            await self.db.rollback()
            self.logger.error(f"Database error while saving banner variant: {str(e)}")
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Unexpected error while saving banner variant: {str(e)}")
            raise
