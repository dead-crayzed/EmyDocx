"""Sanitization for XML 1.0 compatibility (python-docx requirement)."""
import re

# XML 1.0 allows tab, LF, CR, but not most C0 control chars,
# isolated surrogates, or U+FFFE/U+FFFF noncharacters.
ILLEGAL_XML_CHARS = re.compile(
    r"[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]"
)


def clean_xml_string(value) -> str:
    """Convert value to text and drop characters forbidden by XML 1.0."""
    if value is None:
        return ""
    return ILLEGAL_XML_CHARS.sub("", str(value))