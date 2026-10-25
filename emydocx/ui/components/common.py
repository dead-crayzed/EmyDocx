"""Переиспользуемые мелкие строительные блоки."""
import flet as ft

from emydocx.ui.theme import Colors


def section_title(text: str) -> ft.Text:
    return ft.Text(
        text.upper(), size=10, weight=ft.FontWeight.BOLD, color=Colors.TEXT_SUBTLE,
    )


def make_button(label, icon, handler, primary: bool = False) -> ft.Button:
    return ft.Button(
        content=label,
        icon=icon,
        on_click=handler,
        bgcolor=Colors.ACCENT if primary else "#1E293B",
        color="#FFFFFF",
    )


def divider() -> ft.Divider:
    return ft.Divider(color=Colors.BORDER_SOFT)