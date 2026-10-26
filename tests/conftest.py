"""Общие фикстуры и помощники."""
from io import BytesIO

import pytest
from docx import Document
from docx.oxml.ns import qn

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


def list_properties(document, paragraph):
    """Return the effective DOCX list level, marker format and indentation."""
    num_pr = paragraph._p.pPr.numPr if paragraph._p.pPr is not None else None
    if num_pr is None:
        return None
    num_id = num_pr.numId.val
    level = num_pr.ilvl.val
    numbering = document.part.numbering_part.element
    num = next(
        node for node in numbering.findall(qn("w:num"))
        if int(node.get(qn("w:numId"))) == num_id
    )
    abstract_id = num.find(qn("w:abstractNumId")).get(qn("w:val"))
    abstract = next(
        node for node in numbering.findall(qn("w:abstractNum"))
        if node.get(qn("w:abstractNumId")) == abstract_id
    )
    level_node = next(
        node for node in abstract.findall(qn("w:lvl"))
        if int(node.get(qn("w:ilvl"))) == level
    )
    marker_format = level_node.find(qn("w:numFmt")).get(qn("w:val"))
    indent_twips = int(level_node.find(qn("w:pPr")).find(qn("w:ind")).get(qn("w:left")))
    return num_id, level, marker_format, indent_twips


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
