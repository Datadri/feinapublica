import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import quote

from sqlalchemy.engine.url import make_url

DEFAULT_DATABASE_URL = "sqlite:///./public_jobs_tracker.db"


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


def _is_valid_sqlalchemy_url(url: str) -> bool:
    try:
        make_url(url)
        return True
    except Exception:
        return False


def _encode_credentials_if_needed(url: str) -> str:
    if "://" not in url or "@" not in url:
        return url

    scheme, rest = url.split("://", 1)
    if "/" in rest:
        auth_host, tail = rest.split("/", 1)
        tail = "/" + tail
    else:
        auth_host, tail = rest, ""

    if "@" not in auth_host:
        return url

    auth, host = auth_host.rsplit("@", 1)
    if ":" in auth:
        user, password = auth.split(":", 1)
        auth_encoded = f"{quote(user, safe='')}:{quote(password, safe='')}"
    else:
        auth_encoded = quote(auth, safe="")

    return f"{scheme}://{auth_encoded}@{host}{tail}"


def normalize_database_url(raw_url: str | None) -> str:
    if raw_url is None:
        return DEFAULT_DATABASE_URL

    url = raw_url.strip()
    if not url:
        return DEFAULT_DATABASE_URL

    # Remove accidental surrounding quotes from CI secrets.
    if len(url) >= 2 and ((url[0] == '"' and url[-1] == '"') or (url[0] == "'" and url[-1] == "'")):
        url = url[1:-1].strip()

    # Use psycopg3 driver in SQLAlchemy for PostgreSQL URLs.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://") :]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]

    if _is_valid_sqlalchemy_url(url):
        return url

    encoded = _encode_credentials_if_needed(url)
    if _is_valid_sqlalchemy_url(encoded):
        return encoded

    return url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "dev"),
        database_url=normalize_database_url(os.getenv("DATABASE_URL")),
        cido_base_url=os.getenv("CIDO_BASE_URL", "https://api.diba.cat/dadesobertes/cido/v1"),
        cido_timeout_seconds=_env_int("CIDO_TIMEOUT_SECONDS", 30),
        cido_page_limit=_env_int("CIDO_PAGE_LIMIT", 100),
        cido_max_pages=_env_int("CIDO_MAX_PAGES", 0),
        min_publication_date=os.getenv("MIN_PUBLICATION_DATE", ""),
        default_user_email=os.getenv("DEFAULT_USER_EMAIL", "demo@public-jobs-tracker.local"),
    )


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
