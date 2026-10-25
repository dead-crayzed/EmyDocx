from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
APP_DIR     = PACKAGE_DIR.parent

TEMPLATES_FILE = APP_DIR / "templates.json"

ALLOWED_OPEN_EXTENSIONS = ["md", "markdown", "txt"]
ALLOWED_SAVE_EXTENSIONS = ["md"]

DEFAULT_DOCX_NAME  = "emydocx-document.docx"
DEFAULT_MD_NAME    = "document.md"
DEFAULT_FILE_LABEL = "Новый документ"

WINDOW = {"width": 1320, "height": 850, "min_width": 900, "min_height": 620}

DEFAULT_MARKDOWN = """# EmyDocx — мой первый документ

Это **EmyDocx** — редактор Markdown с экспортом в Word.

## Что умеет прототип

- Редактировать текст в Markdown
- Настраивать шрифты и цвета
- Использовать готовые шаблоны
- Экспортировать документ в DOCX

> Совет: измените текст слева и нажмите «Экспортировать DOCX».

Обычный текст может содержать *курсив*, **жирное выделение** и `код`.
"""