"""Pure helpers — no Flet, no DOCX."""
from pathlib import Path
from typing import Optional

from emydocx.config import DEFAULT_DOCX_NAME, DEFAULT_MD_NAME


def valid_hex(value, fallback: str) -> str:
    """Return '#RRGGBB' if value is a valid 6-digit hex, otherwise fallback."""
    value = (value or "").strip().lstrip("#")
    if len(value) == 6 and all(c in "0123456789abcdefABCDEF" for c in value):
        return "#" + value.upper()
    return fallback


def read_number(value, default: float, minimum: float, maximum: float) -> float:
    """Parse and clamp a numeric setting; return default on any error."""
    try:
        return max(minimum, min(maximum, float(value)))
    except (TypeError, ValueError):
        return default


def suggested_md_name(path: Optional[str]) -> str:
    return Path(path).name if path else DEFAULT_MD_NAME


def suggested_docx_name(path: Optional[str]) -> str:
    return Path(path).stem + ".docx" if path else DEFAULT_DOCX_NAME