from pathlib import Path
import json

import flet as ft

from emydocx.converter import markdown_to_docx


APP_DIR = Path(__file__).resolve().parent
TEMPLATES_FILE = APP_DIR / "templates.json"

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


def load_templates():
    try:
        data = json.loads(TEMPLATES_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data:
            return data
    except (OSError, json.JSONDecodeError):
        pass

    return {
        "Классический": {
            "font_name": "Arial", "body_size": 12, "h1_size": 20,
            "h2_size": 16, "h3_size": 14, "body_color": "#202124",
            "heading_color": "#172554", "margin_cm": 2.0,
            "line_spacing": 1.15,
        },
        "Академический": {
            "font_name": "Times New Roman", "body_size": 14, "h1_size": 16,
            "h2_size": 14, "h3_size": 14, "body_color": "#000000",
            "heading_color": "#000000", "margin_cm": 2.0,
            "line_spacing": 1.5,
        },
        "Минималистичный": {
            "font_name": "Arial", "body_size": 11, "h1_size": 22,
            "h2_size": 17, "h3_size": 14, "body_color": "#30343B",
            "heading_color": "#2563EB", "margin_cm": 1.8,
            "line_spacing": 1.15,
        },
    }


def valid_hex(value, fallback):
    value = (value or "").strip().lstrip("#")
    if len(value) == 6 and all(c in "0123456789abcdefABCDEF" for c in value):
        return "#" + value.upper()
    return fallback


def main(page: ft.Page):
    page.title = "EmyDocx"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B1020"
    page.padding = 0
    page.spacing = 0
    page.window.width = 1320
    page.window.height = 850
    page.window.min_width = 900
    page.window.min_height = 620

    templates = load_templates()
    template_names = list(templates.keys())
    state = {"path": None}

    editor = ft.TextField(
        value=DEFAULT_MARKDOWN,
        multiline=True,
        min_lines=20,
        max_lines=1000,
        expand=True,
        text_size=14,
        border=ft.NoInputBorder(),
        bgcolor="#111827",
        color="#E5E7EB",
        cursor_color="#60A5FA",
        selection_color="#334155",
        content_padding=16,
        hint_text="Введите Markdown здесь...",
    )

    status = ft.Text("Готово к работе", size=12, color="#94A3B8")
    file_label = ft.Text("Новый документ", size=12, color="#94A3B8", max_lines=1)

    template_dropdown = ft.Dropdown(
        label="Шаблон оформления",
        options=[ft.DropdownOption(key=name, text=name) for name in template_names],
        value=template_names[0] if template_names else None,
        dense=True,
        text_size=13,
        border_color="#334155",
    )

    font_dropdown = ft.Dropdown(
        label="Шрифт",
        options=[
            ft.DropdownOption(key=name, text=name)
            for name in ("Arial", "Calibri", "Times New Roman", "Aptos", "Liberation Serif")
        ],
        value="Arial",
        dense=True,
        text_size=13,
        border_color="#334155",
    )

    body_size = ft.TextField(label="Основной текст, pt", value="12", dense=True)
    h1_size = ft.TextField(label="Заголовок 1, pt", value="20", dense=True)
    h2_size = ft.TextField(label="Заголовок 2, pt", value="16", dense=True)
    h3_size = ft.TextField(label="Заголовок 3, pt", value="14", dense=True)
    body_color = ft.TextField(label="Цвет текста (#RRGGBB)", value="#202124", dense=True)
    heading_color = ft.TextField(label="Цвет заголовков (#RRGGBB)", value="#172554", dense=True)
    margin_cm = ft.TextField(label="Поля страницы, см", value="2.0", dense=True)
    line_spacing = ft.Dropdown(
        label="Межстрочный интервал",
        options=[ft.DropdownOption(key=v, text=v) for v in ("1.0", "1.15", "1.5", "2.0")],
        value="1.15",
        dense=True,
        text_size=13,
        border_color="#334155",
    )

    file_picker = ft.FilePicker()
    page.services.append(file_picker)


    def read_number(field, default, minimum, maximum):
        try:
            raw_value = field.value if hasattr(field, "value") else field
            value = float(raw_value)
            return max(minimum, min(maximum, value))
        except (TypeError, ValueError):
            return default


    def get_settings():
        return {
            "font_name": font_dropdown.value or "Arial",
            "body_size": read_number(body_size, 12, 6, 72),
            "h1_size": read_number(h1_size, 20, 6, 72),
            "h2_size": read_number(h2_size, 16, 6, 72),
            "h3_size": read_number(h3_size, 14, 6, 72),
            "body_color": valid_hex(body_color.value, "#202124"),
            "heading_color": valid_hex(heading_color.value, "#172554"),
            "margin_cm": read_number(margin_cm, 2.0, 0.5, 5.0),
            "line_spacing": read_number(line_spacing.value, 1.15, 1.0, 2.0),
        }

    def set_status(message):
        status.value = message
        page.update()

    def apply_template(name):
        data = templates.get(name)
        if not data:
            return
        font_dropdown.value = data.get("font_name", "Arial")
        body_size.value = str(data.get("body_size", 12))
        h1_size.value = str(data.get("h1_size", 20))
        h2_size.value = str(data.get("h2_size", 16))
        h3_size.value = str(data.get("h3_size", 14))
        body_color.value = data.get("body_color", "#202124")
        heading_color.value = data.get("heading_color", "#172554")
        margin_cm.value = str(data.get("margin_cm", 2.0))
        line_spacing.value = str(data.get("line_spacing", 1.15))

    def on_template_change(e):
        apply_template(e.control.value)
        set_status(f"Применён шаблон: {e.control.value}")

    template_dropdown.on_change = on_template_change
    if template_names:
        apply_template(template_names[0])

    async def open_markdown(e):
        try:
            picked = await file_picker.pick_files(
                dialog_title="Открыть Markdown-файл",
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["md", "markdown", "txt"],
                with_data=True,
            )
            if not picked:
                return
            selected = picked[0]
            if selected.bytes is not None:
                content = selected.bytes.decode("utf-8-sig", errors="replace")
            elif getattr(selected, "path", None):
                content = Path(selected.path).read_text(encoding="utf-8-sig")
            else:
                raise RuntimeError("Flet не вернул содержимое файла.")
            editor.value = content
            state["path"] = getattr(selected, "path", None)
            file_label.value = selected.name
            set_status(f"Открыт файл: {selected.name}")
        except Exception as exc:
            set_status(f"Ошибка открытия файла: {exc}")

    async def save_markdown(e):
        try:
            old_path = state["path"]
            suggested_name = Path(old_path).name if old_path else "document.md"
            result = await file_picker.save_file(
                dialog_title="Сохранить Markdown",
                file_name=suggested_name,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["md"],
                src_bytes=(editor.value or "").encode("utf-8"),
            )
            if result:
                state["path"] = result
                file_label.value = Path(result).name
                set_status(f"Markdown сохранён: {result}")
            elif page.web:
                set_status("Файл подготовлен к скачиванию")
        except Exception as exc:
            set_status(f"Ошибка сохранения Markdown: {exc}")


    async def export_docx(e):
        try:
            content = markdown_to_docx(editor.value or "", get_settings())

            old_path = state["path"]
            suggested_name = (
                Path(old_path).stem + ".docx"
                if old_path
                else "emydocx-document.docx"
            )

            result = await file_picker.save_file(
                dialog_title="Экспортировать документ Word",
                file_name=suggested_name,
                src_bytes=content,
            )

            if result:
                set_status(f"DOCX сохранён: {result}")
            elif page.web:
                set_status("Документ подготовлен к скачиванию")

        except Exception as exc:
            import traceback
            traceback.print_exc()
            set_status(f"Ошибка экспорта DOCX: {exc}")


    def new_document(e):
        editor.value = ""
        state["path"] = None
        file_label.value = "Новый документ"
        set_status("Создан новый документ")

    def focus_editor(e):
        editor.focus()
        set_status("Можно вставить текст сочетанием Ctrl+V")

    def section_title(value):
        return ft.Text(value.upper(), size=10, weight=ft.FontWeight.BOLD, color="#64748B")

    def make_button(label, icon, handler, primary=False):
        return ft.Button(
            content=label,
            icon=icon,
            on_click=handler,
            bgcolor="#2563EB" if primary else "#1E293B",
            color="#FFFFFF",
        )

    topbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
        bgcolor="#0F172A",
        border=ft.Border(bottom=ft.BorderSide(1, "#1E293B")),
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("E", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    bgcolor="#2563EB",
                    width=38,
                    height=38,
                    alignment=ft.Alignment.CENTER,
                    border_radius=10,
                ),
                ft.Column(
                    controls=[
                        ft.Text("EmyDocx", size=18, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                        ft.Text("MARKDOWN → WORD", size=9, color="#64748B", weight=ft.FontWeight.BOLD),
                    ],
                    spacing=1,
                ),
                ft.Container(width=8),
                file_label,
                ft.Container(expand=True),
                make_button("Новый", ft.Icons.ADD, new_document),
                make_button("Открыть .md", ft.Icons.FOLDER_OPEN, open_markdown),
                make_button("Сохранить .md", ft.Icons.SAVE, save_markdown),
                make_button("Экспортировать DOCX", ft.Icons.FILE_DOWNLOAD, export_docx, True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
    )

    editor_panel = ft.Container(
        expand=True,
        padding=16,
        content=ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Markdown", size=14, weight=ft.FontWeight.BOLD, color="#E2E8F0"),
                        ft.Container(expand=True),
                        ft.Text("UTF-8", size=10, color="#64748B"),
                    ]
                ),
                ft.Container(
                    content=editor,
                    expand=True,
                    bgcolor="#111827",
                    border=ft.Border.all(1, "#243044"),
                    border_radius=10,
                    padding=8,
                ),
                ft.Text(
                    "Поддерживаются заголовки, списки, цитаты, ссылки, жирный и курсивный текст.",
                    size=11,
                    color="#64748B",
                ),
            ],
        ),
    )

    settings_panel = ft.Container(
        width=330,
        padding=16,
        bgcolor="#0F172A",
        border=ft.Border(left=ft.BorderSide(1, "#1E293B")),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            controls=[
                ft.Text("Экспорт и оформление", size=15, weight=ft.FontWeight.BOLD, color="#F8FAFC"),
                ft.Text("Настройки применяются при создании DOCX.", size=11, color="#94A3B8"),
                ft.Divider(color="#243044"),
                section_title("Быстрый старт"),
                template_dropdown,
                make_button("Применить шаблон", ft.Icons.AUTO_AWESOME,
                            lambda e: on_template_change(type("Event", (), {"control": template_dropdown})())),
                ft.Divider(color="#243044"),
                section_title("Типографика"),
                font_dropdown,
                ft.Row(controls=[ft.Container(content=body_size, expand=True), ft.Container(content=h1_size, expand=True)], spacing=8),
                ft.Row(controls=[ft.Container(content=h2_size, expand=True), ft.Container(content=h3_size, expand=True)], spacing=8),
                ft.Divider(color="#243044"),
                section_title("Цвета"),
                body_color,
                heading_color,
                ft.Divider(color="#243044"),
                section_title("Страница"),
                margin_cm,
                line_spacing,
                ft.Container(height=6),
                ft.Container(
                    bgcolor="#111827",
                    padding=12,
                    border_radius=9,
                    border=ft.Border.all(1, "#243044"),
                    content=ft.Column(
                        spacing=5,
                        controls=[
                            ft.Text("Локальная обработка", size=12, weight=ft.FontWeight.BOLD, color="#CBD5E1"),
                            ft.Text(
                                "Текст не отправляется на сервер. DOCX создаётся на вашем устройстве.",
                                size=11,
                                color="#94A3B8",
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    footer = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        bgcolor="#0F172A",
        border=ft.Border(top=ft.BorderSide(1, "#1E293B")),
        content=ft.Row(
            controls=[
                ft.Container(width=7, height=7, bgcolor="#22C55E", border_radius=10),
                status,
                ft.Container(expand=True),
                ft.Text("EmyDocx • MVP 0.1", size=11, color="#475569"),
            ],
        ),
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                topbar,
                ft.Row(
                    expand=True,
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[editor_panel, settings_panel],
                ),
                footer,
            ],
        )
    )


if __name__ == "__main__":
    ft.run(main)
