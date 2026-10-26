"""UI-компоненты. Без реальной Flet-страницы — только объектные свойства."""
import flet as ft

from emydocx.ui.theme import Colors
from emydocx.ui.components.common import divider, make_button, section_title
from emydocx.ui.components.editor_panel import EditorPanel
from emydocx.ui.components.footer import build_footer
from emydocx.ui.components.settings_panel import SettingsPanel
from emydocx.ui.components.topbar import build_topbar


# ---------- common ----------

def test_section_title_uppercased():
    t = section_title("hello")
    assert t.value == "HELLO"
    assert t.color == Colors.TEXT_SUBTLE


def test_make_button_primary():
    b = make_button("label", ft.Icons.ADD, lambda e: None, primary=True)
    assert b.bgcolor == Colors.ACCENT


def test_make_button_secondary():
    b = make_button("label", ft.Icons.SAVE, lambda e: None, primary=False)
    assert b.bgcolor == "#1E293B"


def test_divider_color():
    d = divider()
    assert d.color == Colors.BORDER_SOFT


# ---------- EditorPanel ----------

def test_editor_panel_initial_value():
    panel = EditorPanel("# start")
    assert panel.value == "# start"


def test_editor_panel_set_value():
    panel = EditorPanel("old")
    panel.value = "new"
    assert panel.value == "new"
    assert panel.editor.value == "new"


def test_editor_panel_none_becomes_empty():
    panel = EditorPanel(None)
    assert panel.value == ""


def test_editor_panel_control_is_container():
    panel = EditorPanel("x")
    assert isinstance(panel.control, ft.Container)


# ---------- SettingsPanel ----------

def _sample_templates():
    return {
        "Default": {
            "font_name": "Arial", "body_size": 12,
            "h1_size": 20, "h2_size": 16, "h3_size": 14,
            "body_color": "#202124", "heading_color": "#172554",
            "margin_cm": 2.0, "line_spacing": 1.15,
        },
        "Academic": {
            "font_name": "Times New Roman", "body_size": 14,
            "h1_size": 24, "h2_size": 18, "h3_size": 16,
            "body_color": "#000000", "heading_color": "#000080",
            "margin_cm": 2.5, "line_spacing": 1.5,
        },
    }


def test_settings_panel_empty_templates():
    """Пустой словарь шаблонов — панель строится."""
    panel = SettingsPanel(templates={})
    assert isinstance(panel.control, ft.Container)
    assert panel.template_dropdown.value is None


def test_settings_panel_first_template_applied():
    panel = SettingsPanel(templates=_sample_templates())
    assert panel.template_dropdown.value == "Default"
    assert panel.font_dropdown.value == "Arial"
    assert panel.body_size.value == "12"


def test_settings_panel_apply_academic():
    panel = SettingsPanel(templates=_sample_templates())
    panel.template_dropdown.value = "Academic"
    panel.apply_current_template()
    assert panel.font_dropdown.value == "Times New Roman"
    assert panel.body_size.value == "14"
    assert panel.margin_cm.value == "2.5"
    assert panel.line_spacing.value == "1.5"


def test_settings_panel_callback_fires():
    calls = []
    panel = SettingsPanel(
        templates=_sample_templates(),
        on_template_applied=calls.append,
    )
    panel.template_dropdown.value = "Academic"
    panel.apply_current_template()
    assert calls == ["Academic"]


def test_settings_panel_no_callback_on_same():
    calls = []
    SettingsPanel(
        templates=_sample_templates(),
        on_template_applied=calls.append,
    )
    # Первое применение из __init__ НЕ идёт через callback
    assert calls == []


def test_settings_panel_get_settings_defaults():
    panel = SettingsPanel(templates=_sample_templates())
    s = panel.get_settings()
    assert s["font_name"] == "Arial"
    assert s["body_size"] == 12
    assert s["h1_size"] == 20
    assert s["h2_size"] == 16
    assert s["h3_size"] == 14
    assert s["body_color"] == "#202124"
    assert s["heading_color"] == "#172554"
    assert s["margin_cm"] == 2.0
    assert s["line_spacing"] == 1.15


def test_settings_panel_get_settings_invalid_hex():
    panel = SettingsPanel(templates=_sample_templates())
    panel.body_color.value = "garbage"
    s = panel.get_settings()
    assert s["body_color"] == "#202124"


def test_settings_panel_get_settings_clamps_size():
    panel = SettingsPanel(templates=_sample_templates())
    panel.body_size.value = "1000"
    assert panel.get_settings()["body_size"] == 72


def test_settings_panel_get_settings_clamps_margin():
    panel = SettingsPanel(templates=_sample_templates())
    panel.margin_cm.value = "0.1"
    assert panel.get_settings()["margin_cm"] == 0.5


def test_settings_panel_get_settings_bad_number_uses_default():
    panel = SettingsPanel(templates=_sample_templates())
    panel.body_size.value = "not-a-number"
    assert panel.get_settings()["body_size"] == 12


# ---------- topbar / footer ----------

def _noop(e):
    return None


def test_topbar_builds():
    label = ft.Text("test.md")
    bar = build_topbar(label, _noop, _noop, _noop, _noop)
    assert isinstance(bar, ft.Container)
    # file_label включён в содержимое
    row = bar.content
    assert label in row.controls


def test_topbar_has_four_buttons():
    label = ft.Text("x")
    bar = build_topbar(label, _noop, _noop, _noop, _noop)
    buttons = [c for c in bar.content.controls if isinstance(c, ft.Button)]
    assert len(buttons) == 4


def test_footer_builds():
    status = ft.Text("ok")
    footer = build_footer(status)
    assert isinstance(footer, ft.Container)
    assert status in footer.content.controls
