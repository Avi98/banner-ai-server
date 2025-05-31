from http import client
from langchain_openai import ChatOpenAI
from openai import OpenAI
from config.env_variables import get_settings
from google import genai


# TODO: file should be renamed to llm clients,
text_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, max_tokens=2000)
openai_client = OpenAI()


def initialize_gemini(content=None, config=None):
    """initialize gemini llm and returns model instance"""

    settings = get_settings()
    generation_model = "gemini-2.5-flash-preview-05-20"
    client = genai.Client(
        vertexai=True,
        project=settings.google_project_id,
        location=settings.google_server_location,
    )

    return client.models.generate_content(
        model=generation_model, contents=content, config=config
    )


def initialize_imagen(**model_config):
    """initialize imagen llm for image edit"""

    settings = get_settings()
    client = genai.Client(
        vertaxai=True,
        project=settings.google_project_id,
        location=settings.google_application_credentials,
    )

    return client.models.generate_content(
        model="imagen-3.0-generate-002", **model_config
    )
