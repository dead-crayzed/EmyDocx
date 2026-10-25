"""Верхняя панель: логотип, имя файла, кнопки действий."""
import flet as ft

from emydocx.ui.theme import Colors, Sizes
from emydocx.ui.components.common import make_button


def build_topbar(
    file_label: ft.Text,
    on_new,
    on_open,
    on_save,
    on_export,
) -> ft.Container:
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
        bgcolor=Colors.PANEL_BG,
        border=ft.Border(bottom=ft.BorderSide(1, Colors.BORDER)),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Container(
                    content=ft.Text("E", size=20, weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF"),
                    bgcolor=Colors.ACCENT,
                    width=Sizes.LOGO, height=Sizes.LOGO,
                    alignment=ft.Alignment.CENTER,
                    border_radius=Sizes.RADIUS,
                ),
                ft.Column(
                    spacing=1,
                    controls=[
                        ft.Text("EmyDocx", size=18, weight=ft.FontWeight.BOLD,
                                color=Colors.TEXT_STRONG),
                        ft.Text("MARKDOWN → WORD", size=9, color=Colors.TEXT_SUBTLE,
                                weight=ft.FontWeight.BOLD),
                    ],
                ),
                ft.Container(width=8),
                file_label,
                ft.Container(expand=True),
                make_button("Новый", ft.Icons.ADD, on_new),
                make_button("Открыть .md", ft.Icons.FOLDER_OPEN, on_open),
                make_button("Сохранить .md", ft.Icons.SAVE, on_save),
                make_button("Экспортировать DOCX", ft.Icons.FILE_DOWNLOAD, on_export,
                            primary=True),
            ],
        ),
    )