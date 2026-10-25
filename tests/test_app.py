"""Интеграционные тесты EmyDocxApp с Mock-страницей."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import flet as ft
import pytest

from emydocx.config import DEFAULT_FILE_LABEL, DEFAULT_MARKDOWN


@pytest.fixture
def make_app(monkeypatch):
    """Фабрика EmyDocxApp с Mock-страницей и заданными шаблонами."""
    def _make(templates=None):
        if templates is None:
            templates = {
                "Default": {
                    "font_name": "Arial", "body_size": 12,
                    "h1_size": 20, "h2_size": 16, "h3_size": 14,
                    "body_color": "#202124", "heading_color": "#172554",
                    "margin_cm": 2.0, "line_spacing": 1.15,
                },
            }
        monkeypatch.setattr(
            "emydocx.app.load_templates", lambda p: templates,
        )
        # Изолируем FilePicker от реального Flet-инстанса
        monkeypatch.setattr("emydocx.app.ft.FilePicker", MagicMock)

        from emydocx.app import EmyDocxApp  # импорт после патча
        page = MagicMock()
        page.services = []
        page.window = MagicMock()
        return EmyDocxApp(page)
    return _make


# ---------- Инициализация ----------

def test_app_mounts_ui(make_app):
    app = make_app()
    app.page.add.assert_called_once()
    assert isinstance(app.topbar, ft.Container)
    assert isinstance(app.footer, ft.Container)
    assert app.editor_panel.control is not None
    assert app.settings_panel.control is not None


def test_app_registers_file_picker(make_app):
    app = make_app()
    assert app.file_picker in app.page.services


def test_app_initial_state(make_app):
    app = make_app()
    assert app.state.current_path is None
    assert app.state.document_name == DEFAULT_FILE_LABEL
    assert app.editor_panel.value == DEFAULT_MARKDOWN


def test_app_window_dimensions(make_app):
    app = make_app()
    # Просто убеждаемся, что настройки доходят до окна
    assert app.page.window.width == 1320
    assert app.page.window.height == 850


# ---------- Новый документ ----------

def test_on_new_clears_state(make_app):
    app = make_app()
    app.editor_panel.value = "dirty"
    app.state.set_document("/tmp/x.md", "x.md")
    app.file_label.value = "x.md"

    app._on_new(None)

    assert app.editor_panel.value == ""
    assert app.state.current_path is None
    assert app.state.document_name == DEFAULT_FILE_LABEL
    assert app.file_label.value == DEFAULT_FILE_LABEL
    assert "Создан" in app.status.value


# ---------- Открытие ----------

def test_on_open_success(make_app):
    app = make_app()
    app.file_picker.pick_files = AsyncMock(return_value=[
        SimpleNamespace(name="doc.md", bytes=b"# hi", path="/tmp/doc.md"),
    ])
    asyncio.run(app._on_open(None))
    assert app.editor_panel.value == "# hi"
    assert app.state.current_path == "/tmp/doc.md"
    assert app.state.document_name == "doc.md"
    assert app.file_label.value == "doc.md"
    assert "Открыт" in app.status.value


def test_on_open_cancel(make_app):
    app = make_app()
    app.file_picker.pick_files = AsyncMock(return_value=[])
    asyncio.run(app._on_open(None))
    assert app.editor_panel.value == DEFAULT_MARKDOWN
    assert app.state.current_path is None


def test_on_open_error(make_app):
    app = make_app()
    app.file_picker.pick_files = AsyncMock(side_effect=RuntimeError("boom"))
    asyncio.run(app._on_open(None))
    assert "Ошибка открытия" in app.status.value


# ---------- Сохранение ----------

def test_on_save_success(make_app):
    app = make_app()
    app.file_picker.save_file = AsyncMock(return_value="/tmp/out.md")
    asyncio.run(app._on_save(None))
    assert app.state.current_path == "/tmp/out.md"
    assert app.file_label.value == "out.md"
    assert "Markdown сохранён" in app.status.value


def test_on_save_uses_existing_name(make_app):
    app = make_app()
    app.state.set_document("/tmp/old.md", "old.md")
    app.file_picker.save_file = AsyncMock(return_value=None)
    asyncio.run(app._on_save(None))
    kwargs = app.file_picker.save_file.call_args.kwargs
    assert kwargs["file_name"] == "old.md"


def test_on_save_web_download_hint(make_app):
    app = make_app()
    app.page.web = True
    app.file_picker.save_file = AsyncMock(return_value=None)
    asyncio.run(app._on_save(None))
    assert "скачиванию" in app.status.value


# ---------- Экспорт ----------

def test_on_export_success(make_app):
    app = make_app()
    app.file_picker.save_file = AsyncMock(return_value="/tmp/out.docx")
    asyncio.run(app._on_export(None))
    assert "DOCX сохранён" in app.status.value


def test_on_export_produces_valid_docx(make_app):
    app = make_app()
    app.file_picker.save_file = AsyncMock(return_value="/tmp/x.docx")
    asyncio.run(app._on_export(None))
    content = app.file_picker.save_file.call_args.kwargs["src_bytes"]
    assert content[:2] == b"PK"
    assert len(content) > 1000


def test_on_export_suggests_docx_name(make_app):
    app = make_app()
    app.state.set_document("/tmp/report.md", "report.md")
    app.file_picker.save_file = AsyncMock(return_value=None)
    asyncio.run(app._on_export(None))
    assert app.file_picker.save_file.call_args.kwargs["file_name"] == "report.docx"


def test_on_export_default_name(make_app):
    app = make_app()
    app.file_picker.save_file = AsyncMock(return_value=None)
    asyncio.run(app._on_export(None))
    assert app.file_picker.save_file.call_args.kwargs["file_name"] == "emydocx-document.docx"


def test_on_export_uses_settings_panel(make_app):
    """Кастомная настройка (h1_size) реально применяется."""
    app = make_app()
    app.settings_panel.h1_size.value = "30"
    app.file_picker.save_file = AsyncMock(return_value=None)
    asyncio.run(app._on_export(None))

    # Проверим, что в созданном DOCX заголовок имеет размер 30
    from io import BytesIO
    from docx import Document

    content = app.file_picker.save_file.call_args.kwargs["src_bytes"]
    doc = Document(BytesIO(content))
    h1 = doc.paragraphs[0]
    assert h1.style.name == "Heading 1"
    assert h1.runs[0].font.size.pt == pytest.approx(30)


# ---------- Статус ----------

def test_set_status_updates_and_pushes(make_app):
    app = make_app()
    app._set_status("hello")
    assert app.status.value == "hello"
    app.page.update.assert_called()


# ---------- Обработчики в целом ----------

def test_status_starts_ready(make_app):
    app = make_app()
    assert "Готов" in app.status.value