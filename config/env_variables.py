from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    app_name: str = "banner_ai_server"
    hf_token: str = ""  # Add this to match .env
    hf_token_inference: str = ""
    qwen_model_endpoint: str = "Qwen/Qwen2.5-Coder-32B-Instruct"
    stable_diffusion_endpoint: str = "stabilityai/stable-diffusion-xl-base-1.0"


settings = Settings()
