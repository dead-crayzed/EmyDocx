"""EmyDocxApp — сборка UI и обработчики действий."""
from pathlib import Path

import flet as ft

from emydocx.config import (
    DEFAULT_FILE_LABEL,
    DEFAULT_MARKDOWN,
    TEMPLATES_FILE,
    WINDOW,
)
from emydocx.converter import markdown_to_docx
from emydocx.services.file_service import FileService
from emydocx.state import AppState
from emydocx.template_service import load_templates
from emydocx.ui.components.editor_panel import EditorPanel
from emydocx.ui.components.footer import build_footer
from emydocx.ui.components.settings_panel import SettingsPanel
from emydocx.ui.components.topbar import build_topbar
from emydocx.ui.theme import Colors
from emydocx.utils import suggested_docx_name, suggested_md_name


class EmyDocxApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = AppState()
        self.templates = load_templates(TEMPLATES_FILE)

        self._setup_page()
        self._build_services()
        self._build_ui()
        self._mount()

    # ---------- настройка ----------

    def _setup_page(self) -> None:
        p = self.page
        p.title = "EmyDocx"
        p.theme_mode = ft.ThemeMode.DARK
        p.bgcolor = Colors.BG
        p.padding = 0
        p.spacing = 0
        p.window.width = WINDOW["width"]
        p.window.height = WINDOW["height"]
        p.window.min_width = WINDOW["min_width"]
        p.window.min_height = WINDOW["min_height"]

    def _build_services(self) -> None:
        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)
        self.file_service = FileService(self.file_picker)

    def _build_ui(self) -> None:
        self.status = ft.Text("Готово к работе", size=12, color=Colors.TEXT_MUTED)
        self.file_label = ft.Text(
            self.state.document_name, size=12,
            color=Colors.TEXT_MUTED, max_lines=1,
        )

        self.editor_panel = EditorPanel(DEFAULT_MARKDOWN)
        self.settings_panel = SettingsPanel(
            self.templates,
            on_template_applied=lambda name: self._set_status(
                f"Применён шаблон: {name}"
            ),
        )

        self.topbar = build_topbar(
            file_label=self.file_label,
            on_new=self._on_new,
            on_open=self._on_open,
            on_save=self._on_save,
            on_export=self._on_export,
        )
        self.footer = build_footer(self.status)

    def _mount(self) -> None:
        self.page.add(
            ft.Column(
                expand=True, spacing=0,
                controls=[
                    self.topbar,
                    ft.Row(
                        expand=True, spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[self.editor_panel.control,
                                  self.settings_panel.control],
                    ),
                    self.footer,
                ],
            )
        )

    # ---------- утилиты ----------

    def _set_status(self, message: str) -> None:
        self.status.value = message
        self.page.update()

    # ---------- обработчики ----------

    def _on_new(self, e) -> None:
        self.editor_panel.value = ""
        self.state.reset()
        self.file_label.value = DEFAULT_FILE_LABEL
        self._set_status("Создан новый документ")

    async def _on_open(self, e) -> None:
        try:
            opened = await self.file_service.open_markdown()
            if opened is None:
                return
            self.editor_panel.value = opened.content
            self.state.set_document(opened.path, opened.name)
            self.file_label.value = opened.name
            self._set_status(f"Открыт файл: {opened.name}")
        except Exception as exc:
            self._set_status(f"Ошибка открытия файла: {exc}")

    async def _on_save(self, e) -> None:
        try:
            result = await self.file_service.save_markdown(
                self.editor_panel.value,
                suggested_md_name(self.state.current_path),
            )
            if result:
                self.state.set_document(result, Path(result).name)
                self.file_label.value = Path(result).name
                self._set_status(f"Markdown сохранён: {result}")
            elif self.page.web:
                self._set_status("Файл подготовлен к скачиванию")
        except Exception as exc:
            self._set_status(f"Ошибка сохранения Markdown: {exc}")

    async def _on_export(self, e) -> None:
        try:
            content = markdown_to_docx(
                self.editor_panel.value,
                self.settings_panel.get_settings(),
            )
            result = await self.file_service.export_docx(
                content,
                suggested_docx_name(self.state.current_path),
            )
            if result:
                self._set_status(f"DOCX сохранён: {result}")
            elif self.page.web:
                self._set_status("Документ подготовлен к скачиванию")
        except Exception as exc:
            import traceback
            traceback.print_exc()
            self._set_status(f"Ошибка экспорта DOCX: {exc}")