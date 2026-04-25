from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 60
    GEMINI_API_KEY: str

    class Config:
        env_file = Path(__file__).parent.parent / ".env"

settings = Settings()