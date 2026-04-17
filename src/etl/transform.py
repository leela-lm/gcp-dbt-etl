import re
import logging
from typing import Optional

log = logging.getLogger(__name__)


def _clean_str(value) -> Optional[str]:
    """Remove leading/trailing whitespace.Return None if empty."""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def _fix_chapter_id(chapter_id : Optional[str]) -> Optional[str]:
    """
    Fix malformed ChapterID values found in source data.
    - "GA0147"  → "GA-0147"  (missing hyphen)
    - "PA-"     → None        (incomplete)
    """
    if not chapter_id:
        return None
    #Insert hyphen if missing eg.GA0147 -> GA-0147
    fixed = re.sub(r'^([A-Z]{2})(\d+)$', r'\1-\2', chapter_id)

    return fixed


def extract_fields(feature: dict) -> Optional[dict]:
    """Turn one raw API feature into a clean flat dictionary."""
    attrs    = feature.get("attributes",{})
    geometry = feature.get("geometry",{})

    longitude    = geometry.get("x")
    latitude     = geometry.get("y")

    return {
        "chapter_id":   _fix_chapter_id(_clean_str(attrs.get("ChapterID"))),
        "chapter_name": _clean_str(attrs.get("University_Chapter")),
        "city":         _clean_str(attrs.get("City")),
        "state":        _clean_str(attrs.get("State")),
        "longitude":    float(longitude) if longitude is not None else None,
        "latitude":     float(latitude) if latitude is not None else None,
    }


def transform_chapters(raw_features: list[dict]) -> list[dict]:
    transformed = [extract_fields(f) for f in raw_features]
    log.info(f"Transformed {len(transformed)} records")
    return transformed