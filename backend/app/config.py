"""Application configuration."""
import logging
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-me-in-production-use-a-strong-random-key"
    DATABASE_URL: str = "sqlite:///./data/learnapp.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000"

    QR_TOKEN_EXPIRE_MINUTES: int = 5
    MAX_CHILDREN_PER_PARENT: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def model_post_init(self, __context):
        if self.SECRET_KEY.startswith("change-me"):
            logging.warning("⚠️ SECRET_KEY is default value! Set a strong key in .env")

    @property
    def cors_origins_list(self):
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
