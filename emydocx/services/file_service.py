"""FilePicker wrapper: open / save / export."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import flet as ft

from emydocx.config import ALLOWED_OPEN_EXTENSIONS, ALLOWED_SAVE_EXTENSIONS


@dataclass
class OpenedFile:
    """Результат открытия файла: имя, содержимое, путь (если известен)."""
    name: str
    content: str
    path: Optional[str]


class FileService:
    def __init__(self, file_picker: ft.FilePicker):
        self.picker = file_picker

    async def open_markdown(self) -> Optional[OpenedFile]:
        picked = await self.picker.pick_files(
            dialog_title="Открыть Markdown-файл",
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=ALLOWED_OPEN_EXTENSIONS,
            with_data=True,
        )
        if not picked:
            return None

        selected = picked[0]
        if selected.bytes is not None:
            content = selected.bytes.decode("utf-8-sig", errors="replace")
        elif getattr(selected, "path", None):
            content = Path(selected.path).read_text(encoding="utf-8-sig")
        else:
            raise RuntimeError("Flet не вернул содержимое файла.")

        return OpenedFile(
            name=selected.name,
            content=content,
            path=getattr(selected, "path", None),
        )

    async def save_markdown(self, content: str, suggested_name: str) -> Optional[str]:
        return await self.picker.save_file(
            dialog_title="Сохранить Markdown",
            file_name=suggested_name,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=ALLOWED_SAVE_EXTENSIONS,
            src_bytes=(content or "").encode("utf-8"),
        )

    async def export_docx(self, content: bytes, suggested_name: str) -> Optional[str]:
        return await self.picker.save_file(
            dialog_title="Экспортировать документ Word",
            file_name=suggested_name,
            src_bytes=content,
        )