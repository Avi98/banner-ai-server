from encodings.base64_codec import base64_decode
from core.model.llm import initialize_gemini
from core.utils.logger import Logger
from services.utils.donload_files import download_files, save_files


# TODO: change this with statement in context with finally as removing the files
class ProductImage:

    file_ids: list[dict[str, str]]
    logger: Logger

    def __init__(self):
        self.logger = Logger.get_logger(__name__, level="INFO")
        self.client = initialize_gemini

    def uploadImg(self, imgPaths: list[str]):
        with open(imgPaths, "rb") as product_content:
            result = self.client.files.create(file=product_content, purpose="vision")
            self.file_ids.append(result.id)

            return self.file_ids

    def save_img_files(self, urls: list[str], img_dir: str) -> list[dict[str, str]]:
        try:
            product_image = download_files(urls, img_dir)
            self.file_ids = product_image

            return self.file_ids

        except Exception as e:
            raise e

    def get_image_file(self, img_paths: list[str], prompt: str, out_dir: str):
        try:

            img_client = self.client({"prompt": prompt})
            return
            save_files(out_dir, file_name="sample_banner_1", img_bytes=img_byes)

        except Exception as e:
            raise e
