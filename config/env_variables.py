import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DOT_ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=DOT_ENV_FILE, case_sensitive=True
    )

    app_name: str = "banner_ai_server"
    google_application_credentials: str = Field(
        default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
        description="Path to the Google Application Credentials JSON file",
    )
    google_project_id: str = Field(
        default=os.getenv("GOOGLE_PROJECT_ID", ""),
        description="Google Cloud Project ID",
    )
    google_server_location: str = Field(
        default=os.getenv("GOOGLE_SERVER_LOCATION", ""),
        description="Google Cloud Server Location",
    )

    # aws S3
    aws_region: str = Field(
        default=os.getenv("AWS_REGION", ""), description="AWS Region"
    )
    s3_bucket_name: str = Field(
        default=os.getenv("S3_BUCKET_NAME", ""), description="S3 Bucket Name"
    )
    aws_access_key_id: str = Field(
        default=os.getenv("AWS_ACCESS_KEY_ID", ""), description="AWS Access Key ID"
    )
    aws_secret_access_key: str = Field(
        default=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        description="AWS Secret Access Key",
    )

    # DB Configuration
    DB_HOST: str = Field(
        default=os.getenv("DB_HOST", "localhost"), description="Database Host"
    )
    DB_PORT: str = Field(
        default=os.getenv("DB_PORT", "5432"), description="Database Port"
    )
    DB_USER: str = Field(
        default=os.getenv("DB_USER", "postgres"), description="Database User"
    )
    DB_PASSWORD: str = Field(
        default=os.getenv("DB_PASSWORD", "postgres"), description="Database Password"
    )
    DB_NAME: str = Field(
        default=os.getenv("DB_NAME", "bannerDb"), description="Database Name"
    )
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", ""), description="Database URL"
    )

    # cors
    ALLOWED_ORIGIN: str = Field(
        default=os.getenv("ALLOWED_ORIGIN", "http://localhost:3000"),
        description="Origins allowed for headers",
    )

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
