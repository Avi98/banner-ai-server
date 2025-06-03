from google import genai
from google.genai import types

from config.env_variables import get_settings


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


def initialize_gemini_img(content=None, config=None):
    settings = get_settings()
    model = "gemini-2.0-flash-preview-image-generation"
    client = genai.Client(
        vertexai=True,
        project=settings.google_project_id,
        location=settings.google_server_location,
    )

    merge_config = None

    if config is None:
        merge_config = {"response_modalities": ["TEXT", "IMAGE"]}
    elif config.__class__ is "dict":
        merge_config = config | {"response_modalities": ["TEXT", "IMAGE"]}

    # merge_conf = config | {"response_modalities": ["TEXT", "IMAGE"]}
    return client.models.generate_content(
        model=model,
        contents=content,
        config=types.GenerateContentConfig(**merge_config),
    )


def initialize_imagen(**model_config):
    """initialize imagen llm for image edit"""

    settings = get_settings()
    client = genai.Client(
        vertexai=True,
        project=settings.google_project_id,
        location=settings.google_application_credentials,
    )

    return client.models.generate_content(
        model="imagen-3.0-generate-002", **model_config
    )
