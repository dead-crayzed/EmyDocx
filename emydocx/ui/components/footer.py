"""Нижний статус-бар."""
import flet as ft

from emydocx.ui.theme import Colors


def build_footer(status: ft.Text) -> ft.Container:
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        bgcolor=Colors.PANEL_BG,
        border=ft.Border(top=ft.BorderSide(1, Colors.BORDER)),
        content=ft.Row(
            controls=[
                ft.Container(width=7, height=7, bgcolor=Colors.SUCCESS, border_radius=10),
                status,
                ft.Container(expand=True),
                ft.Text("EmyDocx • MVP 0.1", size=11, color=Colors.TEXT_DIM),
            ],
        ),
    )