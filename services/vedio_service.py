from typing import Optional

from core.model.llm import init_veo, initialize_imagen
from core.utils.logger import Logger
from routers.banner.request_types import CreateVedioScriptRequest
from services.s3_storage_service import S3StorageService
from global_type.product_base import ProductBase


class VedioService:
    def __init__(
        self,
        #  storage_service: S3StorageService
    ):
        """
        Initialize VedioService with a storage service
        Args:
            storage_service (S3StorageService): Service for handling object storage operations
        """
        self.logger = Logger.get_logger(__name__)
        # self.storage_service = storage_service
        self.logger.info("VedioService initialized successfully")

    # async def upload_vedio(self, file_path: str, product_id: str) -> str:
    #     """Upload video using the storage service"""
    #     try:
    #         self.logger.info(f"Uploading video for product ID: {product_id}")
    #         object_key = f"vedios/{product_id}/{file_path.split('/')[-1]}"

    #         s3_url = await self.storage_service.upload_object(file_path, object_key)
    #         self.logger.info(f"Video uploaded successfully. URL: {s3_url}")
    #         return s3_url

    #     except Exception as e:
    #         self.logger.error(f"Error uploading video: {str(e)}")
    #         raise

    async def remove_vedio(self, product_id: str, s3_key: str) -> bool:
        """Remove video using the storage service"""
        try:
            self.logger.info(f"Removing video for product ID: {product_id}")
            result = await self.storage_service.remove_object(s3_key)

            if result:
                self.logger.info(f"Video removed successfully. Key: {s3_key}")
            else:
                self.logger.warning(f"Failed to remove video. Key: {s3_key}")

            return result

        except Exception as e:
            self.logger.error(f"Error removing video: {str(e)}")
            return False

    async def save_vedio_link(self, product_id: str, s3_url: str) -> bool:
        """Save S3 video link to database"""
        try:
            self.logger.info(f"Saving video link for product ID: {product_id}")

            # TODO: Implement database save logic here
            # This would include:
            # 1. Creating a database connection
            # 2. Inserting/updating the record with product_id and s3_url
            # 3. Committing the transaction

            self.logger.info(
                f"Video link saved successfully for product ID: {product_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error saving video link to database: {str(e)}")
            return False

    async def generate_add_script(self, product_info: Optional[ProductBase]) -> str:
        # initialize_imagen({"contents": ["create a "]})
        prompt = (
            video_ad_prompt
        ) = """
                Create a short, vertical 3D animated ad video for {platform}. The scene opens with a high-energy transition into a futuristic, minimal electronics showroom glowing with cool blue and silver tones. A set of cutting-edge electronics — a frameless smart TV, wireless earbuds, smartwatch, DSLR camera, and sleek smartphone — appear one by one with quick, smooth animations.

                Each product spins slowly or lights up as it enters frame, paired with kinetic text pop-ins that highlight features like:

                “{feature_1}”
                “{feature_2}”
                “{feature_3}”
                “{feature_4}”
                “{feature_5}”

                Use modern techno background music synced to motion beats. The camera transitions quickly between dynamic angles:

                - eye-level pans,
                - close-up shots showing texture and lighting,
                - wide floating angles to give depth and sophistication.

                Color palette: {color_palette}
                Style: {style}
                Lighting: {lighting}
                Ambiance: {ambiance}

                At the end, display a bold call-to-action overlay:
                “{cta_text}”
                with a pulsing button animation and product icons sliding in.

                Aspect Ratio: {aspect_ratio}
                Duration: {duration}
                Target Platform: {target_platform}
                """

        return prompt.format(
            platform="Facebook and Instagram Stories/Reels",
            feature_1="Crystal-Clear 8K Display",
            feature_2="Noise Cancellation Pro",
            feature_3="Smart Sync Watch",
            feature_4="AI Night Camera",
            feature_5="Ultra-Thin Design",
            color_palette="Cool metallic blues, white highlights, neon accents",
            style="Sleek, futuristic, premium tech product showcase",
            lighting="Glowing ambient light with subtle shadows and reflections",
            ambiance="Fast-paced, energetic, and premium-feel",
            cta_text="Shop Now | Limited-Time Deals on Smart Tech",
            aspect_ratio="9:16 (mobile-friendly vertical format)",
            duration="~15 seconds",
            target_platform="Facebook Reels, Instagram Stories, Instagram Reels",
        )

    async def create_vedio(self, prompt: str):

        response = init_veo(contents=prompt)
        return response
