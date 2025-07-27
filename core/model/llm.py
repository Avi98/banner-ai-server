import time
from google import genai
from google.genai import types

from config.env_variables import get_settings


def initialize_gemini(content=None, config=None):
    """initialize gemini llm and returns model instance"""

    settings = get_settings()
    generation_model = "gemini-2.0-flash-lite-001"
    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_PROJECT_ID,
        location=settings.GOOGLE_SERVER_LOCATION,
    )

    return client.models.generate_content(
        model=generation_model, contents=content, config=config
    )


def initialize_gemini_img(content=None, config=None):
    settings = get_settings()
    model = "gemini-2.0-flash-preview-image-generation"
    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_PROJECT_ID,
        location=settings.GOOGLE_SERVER_LOCATION,
    )

    merge_config = None

    if config is None:
        merge_config = {"response_modalities": ["TEXT", "IMAGE"]}
    elif config.__class__ == "dict":
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


def init_veo(contents=None, config=None):
    """Initialize veo client for generating vedio"""

    settings = get_settings()
    model = "veo-2.0-generate-001"
    client = genai.Client(
        vertexai=True,
        project=settings.google_project_id,
        location=settings.google_server_location,
    )

    merge_config = None

    if config is None:
        merge_config = {
            "aspect_ratio": "16:9",  # "16:9" or "9:16"
        }
    elif config.__class__ == "dict":
        merge_config = config | {
            "aspect_ratio": "16:9",  # "16:9" or "9:16"
        }

    operation = client.models.generate_videos(
        model=model,
        prompt=contents,
        config=types.GenerateVideosConfig(**merge_config),
    )

    while not operation.done:
        time.sleep(20)
        operation = client.operations.get(operation)

    for n, generated_video in enumerate(operation.response.generated_videos):
        generated_video.video.save(f"video{n}.mp4")  # save the video

    return "saved"
