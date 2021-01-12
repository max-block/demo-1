from pydantic import BaseSettings

from app import __version__


class AppConfig(BaseSettings):
    app_name: str
    data_dir: str
    access_token: str
    domain: str
    database_url: str
    debug: bool = False
    version: str = __version__

    tags_metadata = [
        {"name": "workers"},
        {"name": "data"},
        {"name": "system"},
        {"name": "telegram"},
        {"name": "auth"},
    ]

    main_menu = {"/ui/workers": "workers", "/ui/data": "data"}

    class Config:
        env_file = ".env"
