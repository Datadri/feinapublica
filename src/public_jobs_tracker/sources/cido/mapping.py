from datetime import date, datetime
from typing import Any

from public_jobs_tracker.utils import normalize_text

# Centralized source-to-domain mapping for CIDO attributes.
# Keep all field name changes localized in this file.
CANDIDATE_FIELDS = {
    "title": ["titol", "title", "nom", "descripcio"],
    "organization": ["ensConvocant", "organisme", "ens_convocant", "denominacioEns", "institucioDesenvolupat"],
    "territory": ["territori", "ambitTerritorial", "nomTerritori", "ambit"],
    "staff_type": ["tipusPersonal", "tipus_personal", "categoriaPersonal"],
    "status": ["estat", "nomEstat", "status"],
    "publication_date": ["dataPublicacio", "maxDataPublicacioDocument", "dataPublicacioDocument"],
    "deadline_date": ["dataFiPresentacio", "dataLimit", "terminiPresentacio", "dataFinalitzacio"],
    "summary": ["objecte", "descripcio", "resum", "observacions"],
    "detail_url": ["urlCido", "urlWeb", "urlConvocatoria", "url", "enllac"],

    # Explicit requested CIDO fields
    "institucio_desenvolupat": ["institucioDesenvolupat"],
    "ambit": ["ambit"],
    "titol": ["titol"],
    "num_places": ["numPlaces"],
    "tipus_personal": ["tipusPersonal"],
    "grup_titulacio": ["grupTitulacio"],
    "sistema_seleccio": ["sistemaSeleccio"],
    "data_finalitzacio": ["dataFinalitzacio"],
    "estat": ["estat"],
    "expedient": ["expedient"],
    "url_web": ["urlWeb"],
}


def _pick_field(payload: dict[str, Any], field_names: list[str]) -> Any:
    attrs = payload.get("attributes", {}) or {}
    for field in field_names:
        if field in attrs and attrs[field] not in (None, ""):
            return attrs[field]
    return None


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    return None


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None
    return None


def map_cido_payload(payload: dict[str, Any]) -> dict[str, Any]:
    attributes = payload.get("attributes", {}) or {}
    links = payload.get("links", {}) or {}

    detail_url = _pick_field(payload, CANDIDATE_FIELDS["detail_url"]) or links.get("self")

    mapped = {
        "source_record_id": str(payload.get("id")) if payload.get("id") is not None else None,

        # Legacy normalized fields
        "title": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["title"])),
        "organization": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["organization"])),
        "territory": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["territory"])),
        "staff_type": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["staff_type"])),
        "status": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["status"])),
        "publication_date": _parse_date(_pick_field(payload, CANDIDATE_FIELDS["publication_date"])),
        "deadline_date": _parse_date(_pick_field(payload, CANDIDATE_FIELDS["deadline_date"])),
        "detail_url": normalize_text(detail_url),
        "summary": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["summary"])),

        # Explicit requested CIDO fields
        "institucio_desenvolupat": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["institucio_desenvolupat"])),
        "ambit": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["ambit"])),
        "titol": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["titol"])),
        "num_places": _parse_int(_pick_field(payload, CANDIDATE_FIELDS["num_places"])),
        "tipus_personal": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["tipus_personal"])),
        "grup_titulacio": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["grup_titulacio"])),
        "sistema_seleccio": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["sistema_seleccio"])),
        "data_finalitzacio": _parse_date(_pick_field(payload, CANDIDATE_FIELDS["data_finalitzacio"])),
        "estat": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["estat"])),
        "expedient": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["expedient"])),
        "url_web": normalize_text(_pick_field(payload, CANDIDATE_FIELDS["url_web"])),

        "raw_attributes": attributes,
    }
    return mapped