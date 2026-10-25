"""Hex → RGBColor with safe fallback."""
from docx.shared import RGBColor


def hex_to_rgb(hex_color, fallback: str = "#202124") -> RGBColor:
    value = (hex_color or fallback).strip().lstrip("#")
    if len(value) != 6:
        value = fallback.lstrip("#")
    try:
        return RGBColor(
            int(value[0:2], 16),
            int(value[2:4], 16),
            int(value[4:6], 16),
        )
    except (ValueError, TypeError):
        return RGBColor(32, 33, 36)