from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    hf_token_inference: str
    qwen_model_endpoint: str
    stable_diffusion_endpoint: str


settings = Settings()
