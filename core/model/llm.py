import time
from typing import Any, Optional, Dict
from google import genai
from google.genai import types

from config.env_variables import get_settings


def initialize_gemini(
    content: Optional[str] = None, config: Optional[Dict[str, Any]] = None
) -> Any:
    """initialize gemini llm and returns model instance"""

    settings = get_settings()
    generation_model = "gemini-2.0-flash-lite-001"
    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_PROJECT_ID,
        location=settings.GOOGLE_SERVER_LOCATION,
    )

    if content is not None:
        return client.models.generate_content(
            model=generation_model, contents=content, config=config #type: ignore
        )


def initialize_gemini_img(
    content: Optional[str] = None, config: Optional[Dict[str, Any]] = None
) -> Any:
    settings = get_settings()
    model = "gemini-2.0-flash-preview-image-generation"
    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_PROJECT_ID,
        location=settings.GOOGLE_SERVER_LOCATION,
    )

    merge_config: Dict[str, Any] = {}

    if config is None:
        merge_config = dict(config or {}) 
        merge_config = {"response_modalities": ["TEXT", "IMAGE"]}

    # merge_conf = config | {"response_modalities": ["TEXT", "IMAGE"]}
    return client.models.generate_content(
        model=model,
        contents=content, #type: ignore
        config=types.GenerateContentConfig(**merge_config),
    )


def initialize_imagen(**model_config: Any) -> Any:
    """initialize imagen llm for image edit"""

    settings = get_settings()
    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_PROJECT_ID,
        location=settings.GOOGLE_SERVER_LOCATION,
    )

    return client.models.generate_content(
        model="imagen-3.0-generate-002", **model_config
    )


def init_veo(
    contents: Optional[str] = None, config: Optional[Dict[str, Any]] = None
) -> Any:
    """Initialize veo client for generating vedio"""

    settings = get_settings()
    model = "veo-2.0-generate-001"
    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_PROJECT_ID,
        location=settings.GOOGLE_SERVER_LOCATION,
    )

    merge_config: Dict[str, Any] = {}

    if config is None:
        merge_config = {
            "aspect_ratio": "16:9",  # "16:9" or "9:16"
        }
    else:
        merge_config = dict(config)
        merge_config["aspect_ratio"] = "16:9"

    operation = client.models.generate_videos(
        model=model,
        prompt=contents,
        config=types.GenerateVideosConfig(**merge_config),
    )

    while not operation.done:
        time.sleep(20)
        operation = client.operations.get(operation)

    if operation.response:
        if operation.response.generated_videos is not None:
            for n, generated_video in enumerate(operation.response.generated_videos):
                if generated_video.video is not None:
                    generated_video.video.save(f"video{n}.mp4")  # save the video

    return "saved"