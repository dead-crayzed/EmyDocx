"""Low-level run (span of text) helpers: font, size, color, formatting."""
from docx.shared import Pt

from emydocx.converter.colors import hex_to_rgb
from emydocx.converter.xml_utils import clean_xml_string


def apply_run_format(run, settings: dict, heading: bool = False, level: int = 0) -> None:
    """Set font name/size/color on a run, honoring heading vs body settings."""
    run.font.name = settings.get("font_name", "Arial")
    if heading:
        size_key = {1: "h1_size", 2: "h2_size", 3: "h3_size"}.get(level, "h3_size")
        run.font.size = Pt(float(settings.get(size_key, settings.get("body_size", 12))))
        run.font.color.rgb = hex_to_rgb(settings.get("heading_color", "#172554"), "#172554")
        run.bold = True
    else:
        run.font.size = Pt(float(settings.get("body_size", 12)))
        run.font.color.rgb = hex_to_rgb(settings.get("body_color", "#202124"), "#202124")


def add_run(paragraph, text, settings: dict, **formatting):
    """Add a sanitized run to paragraph and apply default + extra formatting."""
    run = paragraph.add_run(clean_xml_string(text))
    apply_run_format(run, settings)
    for attribute, value in formatting.items():
        setattr(run, attribute, value)
    return run