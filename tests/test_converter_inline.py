"""Инлайн-форматирование в параграфах."""
import pytest
from docx.shared import RGBColor


def _run_with(paragraph, fragment):
    """Первый run, содержащий fragment."""
    for run in paragraph.runs:
        if fragment in run.text:
            return run
    return None


# ---------- Bold / Italic ----------

def test_bold(settings, render):
    doc = render("Plain **bold** text", settings)
    run = _run_with(doc.paragraphs[0], "bold")
    assert run.bold is True


def test_italic(settings, render):
    doc = render("Plain *italic* text", settings)
    run = _run_with(doc.paragraphs[0], "italic")
    assert run.italic is True


def test_bold_italic(settings, render):
    doc = render("Plain ***both*** text", settings)
    run = _run_with(doc.paragraphs[0], "both")
    assert run.bold is True
    assert run.italic is True


def test_underscore_variants(settings, render):
    doc = render("Plain __bold__ and _it_", settings)
    para = doc.paragraphs[0]
    assert _run_with(para, "bold").bold is True
    assert _run_with(para, "it").italic is True


# ---------- Inline code ----------

def test_inline_code_uses_consolas(settings, render):
    doc = render("Some `code` here", settings)
    run = _run_with(doc.paragraphs[0], "code")
    assert run.font.name == "Consolas"


def test_inline_code_does_not_change_color(settings, render):
    """Код в AST-рендерере — без спеццвета (только шрифт)."""
    doc = render("`x`", settings)
    run = doc.paragraphs[0].runs[0]
    assert run.font.color.rgb == RGBColor(0x20, 0x21, 0x24)


# ---------- Ссылки ----------

def test_link_renders_label_and_url(settings, render):
    doc = render("[Example](https://example.com)", settings)
    text = doc.paragraphs[0].text
    assert "Example" in text
    assert "https://example.com" in text


def test_link_underlined(settings, render):
    doc = render("[x](https://x.test)", settings)
    run = _run_with(doc.paragraphs[0], "x")
    assert run.underline is True


# ---------- Strikethrough ----------

def test_strikethrough(settings, render):
    doc = render("~~deleted~~ text", settings)
    run = _run_with(doc.paragraphs[0], "deleted")
    assert run.font.strike is True


# ---------- Изображения ----------

def test_image_renders_alt(settings, render):
    doc = render("![alt text](image.png)", settings)
    assert "[alt text]" in doc.paragraphs[0].text


# ---------- Переносы ----------

def test_soft_break_becomes_space(settings, render):
    doc = render("line one\nline two", settings)
    # мягкий перенос → пробел в plain_text, но здесь inline_into — softbreak = "\n"
    # Итоговый параграф содержит обе строки
    assert "line one" in doc.paragraphs[0].text
    assert "line two" in doc.paragraphs[0].text


# ---------- Math ----------

def test_inline_math(settings, render):
    doc = render("Text $x^2$ text", settings)
    # math может прийти как текст, не как отдельный run; проверяем что не упало
    assert doc.paragraphs[0] is not None


def test_block_math(settings, render):
    doc = render("$$E = mc^2$$", settings)
    para = doc.paragraphs[0]
    assert "E = mc^2" in para.text
    # Кембрия Math на run'е
    for run in para.runs:
        if run.text.strip():
            assert run.font.name == "Cambria Math"
            assert run.italic is True
            break


# ---------- Комбинации ----------

def test_combination_in_one_paragraph(settings, render):
    md = "**bold** and *italic* and `code` and [link](https://x.test)"
    doc = render(md, settings)
    para = doc.paragraphs[0]
    assert _run_with(para, "bold").bold is True
    assert _run_with(para, "italic").italic is True
    assert _run_with(para, "code").font.name == "Consolas"
    assert _run_with(para, "link").underline is True


def test_heading_with_inline_formatting(settings, render):
    doc = render("# **bold** and *it*", settings)
    para = doc.paragraphs[0]
    assert para.style.name == "Heading 1"
    bold_run = _run_with(para, "bold")
    assert bold_run.bold is True
    # Размер — как у h1, а не как у body
    assert bold_run.font.size.pt == pytest.approx(settings["h1_size"])