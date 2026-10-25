
import json
from pathlib import Path


DEFAULT_TEMPLATES = {
    "Классический": {
        "font_name": "Arial",
        "body_size": 12,
        "h1_size": 20,
        "h2_size": 16,
        "h3_size": 14,
        "body_color": "#202124",
        "heading_color": "#172554",
        "margin_cm": 2.0,
        "line_spacing": 1.15,
    },
    "Академический": {
        "font_name": "Times New Roman",
        "body_size": 14,
        "h1_size": 16,
        "h2_size": 14,
        "h3_size": 14,
        "body_color": "#000000",
        "heading_color": "#000000",
        "margin_cm": 2.0,
        "line_spacing": 1.5,
    },
    "Минималистичный": {
        "font_name": "Arial",
        "body_size": 11,
        "h1_size": 22,
        "h2_size": 17,
        "h3_size": 14,
        "body_color": "#30343B",
        "heading_color": "#2563EB",
        "margin_cm": 1.8,
        "line_spacing": 1.15,
    },
}


def load_templates(path: Path) -> dict:
    """Load document templates or return the built-in defaults."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))

        if isinstance(data, dict) and data:
            return data

    except (OSError, json.JSONDecodeError):
        pass

    return {
        name: settings.copy()
        for name, settings in DEFAULT_TEMPLATES.items()
    }
