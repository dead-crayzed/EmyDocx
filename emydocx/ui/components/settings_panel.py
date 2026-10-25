"""Правая панель экспорта и оформления."""
from typing import Callable, Optional

import flet as ft

from emydocx.ui.theme import Colors, Sizes
from emydocx.ui.components.common import divider, make_button, section_title
from emydocx.utils import read_number, valid_hex


FONT_CHOICES   = ("Arial", "Calibri", "Times New Roman", "Aptos", "Liberation Serif")
LINE_SPACINGS  = ("1.0", "1.15", "1.5", "2.0")


def _outlined() -> ft.OutlineInputBorder:
    return ft.OutlineInputBorder(side=ft.BorderSide(color="#334155", width=1))


class SettingsPanel:
    def __init__(
        self,
        templates: dict,
        on_template_applied: Optional[Callable[[str], None]] = None,
    ):
        self.templates = templates
        self.on_template_applied = on_template_applied

        self._build_controls()
        self._build_container()

        if self.templates:
            first = next(iter(self.templates))
            self.template_dropdown.value = first
            self._apply_template(first)

    # ---------- построение ----------

    def _build_controls(self) -> None:
        self.template_dropdown = ft.Dropdown(
            label="Шаблон оформления",
            options=[ft.DropdownOption(key=n, text=n) for n in self.templates],
            dense=True, text_size=13, border=_outlined(),
        )
        self.template_dropdown.on_change = self._on_template_change

        self.font_dropdown = ft.Dropdown(
            label="Шрифт",
            options=[ft.DropdownOption(key=n, text=n) for n in FONT_CHOICES],
            value="Arial", dense=True, text_size=13, border=_outlined(),
        )

        self.body_size = ft.TextField(label="Основной текст, pt", value="12", dense=True)
        self.h1_size   = ft.TextField(label="Заголовок 1, pt",    value="20", dense=True)
        self.h2_size   = ft.TextField(label="Заголовок 2, pt",    value="16", dense=True)
        self.h3_size   = ft.TextField(label="Заголовок 3, pt",    value="14", dense=True)

        self.body_color    = ft.TextField(label="Цвет текста (#RRGGBB)",
                                          value="#202124", dense=True)
        self.heading_color = ft.TextField(label="Цвет заголовков (#RRGGBB)",
                                          value="#172554", dense=True)

        self.margin_cm = ft.TextField(label="Поля страницы, см", value="2.0", dense=True)
        self.line_spacing = ft.Dropdown(
            label="Межстрочный интервал",
            options=[ft.DropdownOption(key=v, text=v) for v in LINE_SPACINGS],
            value="1.15", dense=True, text_size=13, border=_outlined(),
        )

    def _build_container(self) -> None:
        self.control = ft.Container(
            width=Sizes.PANEL_WIDTH,
            padding=16,
            bgcolor=Colors.PANEL_BG,
            border=ft.Border(left=ft.BorderSide(1, Colors.BORDER)),
            content=ft.Column(
                expand=True, scroll=ft.ScrollMode.AUTO, spacing=10,
                controls=[
                    ft.Text("Экспорт и оформление", size=15,
                            weight=ft.FontWeight.BOLD, color=Colors.TEXT_STRONG),
                    ft.Text("Настройки применяются при создании DOCX.",
                            size=11, color=Colors.TEXT_MUTED),
                    divider(),
                    section_title("Быстрый старт"),
                    self.template_dropdown,
                    make_button("Применить шаблон", ft.Icons.AUTO_AWESOME,
                                self._on_apply_click),
                    divider(),
                    section_title("Типографика"),
                    self.font_dropdown,
                    ft.Row(spacing=8, controls=[
                        ft.Container(content=self.body_size, expand=True),
                        ft.Container(content=self.h1_size,   expand=True),
                    ]),
                    ft.Row(spacing=8, controls=[
                        ft.Container(content=self.h2_size, expand=True),
                        ft.Container(content=self.h3_size, expand=True),
                    ]),
                    divider(),
                    section_title("Цвета"),
                    self.body_color,
                    self.heading_color,
                    divider(),
                    section_title("Страница"),
                    self.margin_cm,
                    self.line_spacing,
                    ft.Container(height=6),
                    self._info_card(),
                ],
            ),
        )

    def _info_card(self) -> ft.Container:
        return ft.Container(
            bgcolor=Colors.EDITOR_BG,
            padding=12, border_radius=9,
            border=ft.Border.all(1, Colors.BORDER_SOFT),
            content=ft.Column(spacing=5, controls=[
                ft.Text("Локальная обработка", size=12,
                        weight=ft.FontWeight.BOLD, color="#CBD5E1"),
                ft.Text("Текст не отправляется на сервер. DOCX создаётся "
                        "на вашем устройстве.",
                        size=11, color=Colors.TEXT_MUTED),
            ]),
        )

    # ---------- шаблоны ----------

    def _on_template_change(self, e) -> None:
        self.apply_current_template()

    def _on_apply_click(self, e) -> None:
        self.apply_current_template()

    def apply_current_template(self) -> None:
        name = self.template_dropdown.value
        if not name:
            return
        self._apply_template(name)
        if self.on_template_applied:
            self.on_template_applied(name)

    def _apply_template(self, name: str) -> None:
        data = self.templates.get(name)
        if not data:
            return
        self.font_dropdown.value    = data.get("font_name", "Arial")
        self.body_size.value        = str(data.get("body_size", 12))
        self.h1_size.value          = str(data.get("h1_size", 20))
        self.h2_size.value          = str(data.get("h2_size", 16))
        self.h3_size.value          = str(data.get("h3_size", 14))
        self.body_color.value       = data.get("body_color", "#202124")
        self.heading_color.value    = data.get("heading_color", "#172554")
        self.margin_cm.value        = str(data.get("margin_cm", 2.0))
        self.line_spacing.value     = str(data.get("line_spacing", 1.15))

    # ---------- настройки на выход ----------

    def get_settings(self) -> dict:
        return {
            "font_name":     self.font_dropdown.value or "Arial",
            "body_size":     read_number(self.body_size.value,   12,   6,  72),
            "h1_size":       read_number(self.h1_size.value,     20,   6,  72),
            "h2_size":       read_number(self.h2_size.value,     16,   6,  72),
            "h3_size":       read_number(self.h3_size.value,     14,   6,  72),
            "body_color":    valid_hex(self.body_color.value,    "#202124"),
            "heading_color": valid_hex(self.heading_color.value, "#172554"),
            "margin_cm":     read_number(self.margin_cm.value,   2.0, 0.5, 5.0),
            "line_spacing":  read_number(self.line_spacing.value, 1.15, 1.0, 2.0),
        }