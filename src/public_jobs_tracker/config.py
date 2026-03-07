import logging
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    cido_base_url: str
    cido_timeout_seconds: int
    cido_page_limit: int
    cido_max_pages: int
    min_publication_date: str
    default_user_email: str


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "dev"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./public_jobs_tracker.db"),
        cido_base_url=os.getenv("CIDO_BASE_URL", "https://api.diba.cat/dadesobertes/cido/v1"),
        cido_timeout_seconds=_env_int("CIDO_TIMEOUT_SECONDS", 30),
        cido_page_limit=_env_int("CIDO_PAGE_LIMIT", 100),
        cido_max_pages=_env_int("CIDO_MAX_PAGES", 0),
        min_publication_date=os.getenv("MIN_PUBLICATION_DATE", ""),
        default_user_email=os.getenv("DEFAULT_USER_EMAIL", "demo@public-jobs-tracker.local"),
    )


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")