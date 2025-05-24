import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


DOT_ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore", env_file=DOT_ENV_FILE)

    app_name: str = "banner_ai_server"
    hf_token: str = ""
    openai_api_key: str
    hf_token_inference: str = ""
    qwen_model_endpoint: str = ""
    stable_diffusion_endpoint: str


def get_settings() -> Settings:
    """
    Get the settings for the application.
    """
    return Settings()
