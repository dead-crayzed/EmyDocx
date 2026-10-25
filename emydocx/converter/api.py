"""Public entry point: markdown_to_docx()."""
from io import BytesIO

from emydocx.converter.document_setup import create_document
from emydocx.converter.parser import parse_markdown
from emydocx.converter.renderer import BlockRenderer


def markdown_to_docx(markdown_text: str, settings: dict) -> bytes:
    """Convert Markdown to a formatted DOCX byte string."""
    document = create_document(settings)
    tokens = parse_markdown(markdown_text)
    BlockRenderer(document, settings).render(tokens)
    output = BytesIO()
    document.save(output)
    return output.getvalue()