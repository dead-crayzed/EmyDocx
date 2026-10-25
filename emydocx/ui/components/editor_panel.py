"""Центральная панель с редактором Markdown."""
import flet as ft

from emydocx.ui.theme import Colors, Sizes


class EditorPanel:
    def __init__(self, initial_value: str):
        self.editor = ft.TextField(
            value=initial_value,
            multiline=True,
            min_lines=20,
            max_lines=1000,
            expand=True,
            text_size=14,
            border=ft.NoInputBorder(),
            bgcolor=Colors.EDITOR_BG,
            color=Colors.TEXT,
            cursor_color=Colors.CURSOR,
            selection_color=Colors.SELECTION,
            content_padding=16,
            hint_text="Введите Markdown здесь...",
        )

        self.control = ft.Container(
            expand=True,
            padding=16,
            content=ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    ft.Row(controls=[
                        ft.Text("Markdown", size=14, weight=ft.FontWeight.BOLD,
                                color="#E2E8F0"),
                        ft.Container(expand=True),
                        ft.Text("UTF-8", size=10, color=Colors.TEXT_SUBTLE),
                    ]),
                    ft.Container(
                        content=self.editor,
                        expand=True,
                        bgcolor=Colors.EDITOR_BG,
                        border=ft.Border.all(1, Colors.BORDER_SOFT),
                        border_radius=Sizes.RADIUS,
                        padding=8,
                    ),
                    ft.Text(
                        "Поддерживаются заголовки, списки, цитаты, ссылки, "
                        "жирный и курсивный текст.",
                        size=11, color=Colors.TEXT_SUBTLE,
                    ),
                ],
            ),
        )

    @property
    def value(self) -> str:
        return self.editor.value or ""

    @value.setter
    def value(self, v: str) -> None:
        self.editor.value = v

    def focus(self) -> None:
        self.editor.focus()