"""Regex-based inline formatter — fallback for raw HTML / unknown blocks."""
import re

from emydocx.converter.colors import hex_to_rgb
from emydocx.converter.runs import add_run
from emydocx.converter.xml_utils import clean_xml_string


INLINE_PATTERN = re.compile(
    r"(\*\*\*.+?\*\*\*|___.+?___|\*\*.+?\*\*|__.+?__|"
    r"\*[^*\n]+?\*|_[^_\n]+?_|`[^`\n]+`|"
    r"\[([^\]]+)\]\(([^)]+)\))"
)


def add_inline_regex(paragraph, text, settings, base_bold: bool = False, base_italic: bool = False) -> None:
    text = clean_xml_string(text)
    pos = 0
    for match in INLINE_PATTERN.finditer(text):
        if match.start() > pos:
            add_run(paragraph, text[pos:match.start()], settings,
                    bold=base_bold, italic=base_italic)

        token = match.group(0)
        if (token.startswith("***") and token.endswith("***")) or (
            token.startswith("___") and token.endswith("___")
        ):
            add_run(paragraph, token[3:-3], settings, bold=True, italic=True)
        elif token.startswith("**") or token.startswith("__"):
            add_run(paragraph, token[2:-2], settings, bold=True)
        elif token.startswith("*") or token.startswith("_"):
            add_run(paragraph, token[1:-1], settings, italic=True)
        elif token.startswith("`"):
            run = add_run(paragraph, token[1:-1], settings)
            run.font.name = "Consolas"
            run.font.color.rgb = hex_to_rgb("#7C3AED")
        else:
            label, url = match.group(2), match.group(3)
            run = add_run(paragraph, f"{label} ({url})", settings)
            run.underline = True
        pos = match.end()

    if pos < len(text):
        add_run(paragraph, text[pos:], settings,
                bold=base_bold, italic=base_italic)