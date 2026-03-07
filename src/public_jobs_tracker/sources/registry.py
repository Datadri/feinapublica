from public_jobs_tracker.sources.base import SourceClient
from public_jobs_tracker.sources.cido.client import CidoClient


def get_source_client(source_name: str) -> SourceClient:
    registry: dict[str, type[SourceClient]] = {
        "cido": CidoClient,
    }
    if source_name not in registry:
        raise ValueError(f"Unsupported source: {source_name}")
    return registry[source_name]()
