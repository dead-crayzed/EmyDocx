"""Create and configure the base Document (margins, Normal style)."""
from docx import Document
from docx.shared import Cm, Pt

from emydocx.converter.colors import hex_to_rgb


def create_document(settings: dict) -> Document:
    document = Document()
    section = document.sections[0]
    margin = Cm(float(settings.get("margin_cm", 2.0)))
    section.top_margin = margin
    section.bottom_margin = margin
    section.left_margin = margin
    section.right_margin = margin

    normal = document.styles["Normal"]
    normal.font.name = settings.get("font_name", "Arial")
    normal.font.size = Pt(float(settings.get("body_size", 12)))
    normal.font.color.rgb = hex_to_rgb(settings.get("body_color", "#202124"))
    normal.paragraph_format.line_spacing = float(settings.get("line_spacing", 1.15))
    normal.paragraph_format.space_after = Pt(6)
    return document