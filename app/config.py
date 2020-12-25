from pydantic import BaseSettings

from app import __version__


class AppConfig(BaseSettings):
    APP_NAME: str
    DATA_DIR: str
    ACCESS_TOKEN: str
    DOMAIN: str
    DATABASE_URL: str
    DEBUG: bool = False
    VERSION: str = __version__

    TAGS_METADATA = [
        {"name": "workers"},
        {"name": "data"},
        {"name": "system"},
        {"name": "auth"},
    ]

    class Config:
        env_file = ".env"
