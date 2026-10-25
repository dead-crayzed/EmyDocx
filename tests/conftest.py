"""Общие фикстуры и помощники."""
from io import BytesIO

import pytest
from docx import Document

from emydocx.converter import markdown_to_docx


DEFAULT_SETTINGS = {
    "font_name": "Arial",
    "body_size": 12,
    "h1_size": 20,
    "h2_size": 16,
    "h3_size": 14,
    "body_color": "#202124",
    "heading_color": "#172554",
    "margin_cm": 2.0,
    "line_spacing": 1.15,
}


@pytest.fixture
def settings() -> dict:
    """Свежая копия дефолтных настроек на каждый тест."""
    return dict(DEFAULT_SETTINGS)


@pytest.fixture
def render():
    """markdown → python-docx Document (для инспекции)."""
    def _render(md: str, s: dict) -> Document:
        return Document(BytesIO(markdown_to_docx(md, s)))
    return _render