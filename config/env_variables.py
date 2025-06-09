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
    google_application_credentials: str
    google_project_id: str
    google_server_location: str

    # aws S3
    aws_region: str = ""
    s3_bucket_name: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # DB Configuration
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "bannerDb"
    DATABASE_URL: str = ""

    @property
    def get_database_url(self) -> str:
        """
        Constructs and returns the database URL using the individual components
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


def get_settings() -> Settings:
    """
    Get the settings for the application.
    """
    return Settings()
