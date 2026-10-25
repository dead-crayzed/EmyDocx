"""Markdown → Mistune AST parsing (tables, strikethrough, math enabled)."""
import mistune

from emydocx.converter.xml_utils import clean_xml_string


def parse_markdown(markdown_text: str) -> list:
    markdown = mistune.create_markdown(
        renderer="ast",
        plugins=["table", "strikethrough", "math", "task_lists"],
    )
    return markdown(clean_xml_string(markdown_text or ""))