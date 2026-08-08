import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Safarnama"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(os.getcwd(), 'db/safarnama_v2.db')}"
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_must_be_long_and_secure")

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()
