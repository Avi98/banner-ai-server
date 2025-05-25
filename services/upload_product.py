from openai import OpenAI
from core.agent.llm import openai_client


# TODO: change this with statement in context with finally as removing the files
class ProductImage:

    client: OpenAI = openai_client
    file_ids: list[str] = []

    def uploadImg(self, imgPaths: list[str]):
        with open(imgPaths, "rb") as product_content:
            result = self.client.files.create(file=product_content, purpose="vision")
            self.file_ids.append(result.id)

            return self.file_ids
