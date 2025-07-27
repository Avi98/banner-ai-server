from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DOT_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=DOT_ENV_FILE, case_sensitive=True
    )

    app_name: str = "banner_ai_server"
    GOOGLE_PROJECT_ID: str = Field(description="Google Cloud Project ID")
    GOOGLE_SERVER_LOCATION: str = Field(description="Google Cloud Server Location")

    # aws S3
    AWS_REGION: str = Field(default="", description="AWS Region")
    S3_BUCKET_NAME: str = Field(default="", description="S3 Bucket Name")
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS Secret Access Key")

    # DB Configuration
    DB_HOST: str = Field(description="Database Host")
    DB_PORT: str = Field(description="Database Port")
    DB_USER: str = Field(description="Database User")
    DB_PASSWORD: str = Field(description="Database Password")
    DB_NAME: str = Field(description="Database Name")
    DATABASE_URL: str = Field(default="", description="Database URL")

    # cors
    ALLOWED_ORIGIN: str = Field(
        default="http://localhost:3000", description="Origins allowed for headers"
    )

    @property
    def get_database_url(self) -> str:
        """
        Constructs and returns the database URL using the individual components
        """
        # return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}"


def get_settings() -> Settings:
    """
    Get the settings for the application.
    """
    return Settings()
