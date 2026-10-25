"""AST-to-DOCX renderer: walks Mistune tokens and fills a Document."""
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from emydocx.converter.numbering import NumberingManager

from emydocx.converter.colors import hex_to_rgb
from emydocx.converter.legacy_inline import add_inline_regex
from emydocx.converter.runs import add_run, apply_run_format
from emydocx.converter.xml_utils import clean_xml_string
from emydocx.converter.latex import MATH_TOKEN, latex_to_unicode


class BlockRenderer:
    """Renders a Mistune AST into an existing python-docx Document."""

    def __init__(self, document, settings: dict):
        self.document = document
        self.settings = settings
        self.numbering = NumberingManager(document)

    # ---------- public ----------

    def render(self, tokens) -> None:
        self._add_blocks(tokens)

    # ---------- plain text ----------

    def _image_alt(self, child) -> str:
        """Mistune 3.x кладёт alt в children; attrs.alt поддерживаем на всякий."""
        attrs_alt = child.get("attrs", {}).get("alt")
        if attrs_alt:
            return attrs_alt
        return self._plain_text(child.get("children") or [])


    def _plain_text(self, children) -> str:
        parts = []
        for child in children or []:
            kind = child.get("type")
            if kind in ("text", "codespan", "inline_html", "inline_math", "block_math"):
                parts.append(child.get("raw", ""))
            elif kind in ("strong", "emphasis", "link", "strikethrough"):
                parts.append(self._plain_text(child.get("children")))
            elif kind == "image":
                parts.append(self._image_alt(child))
            elif kind == "softbreak":
                parts.append(" ")
            elif kind == "linebreak":
                parts.append("\n")
            elif kind == "table_cell":
                parts.append(self._plain_text(child.get("children", [])))
        return clean_xml_string("".join(parts))

    # ---------- runs / inline ----------

    def _add_run(self, paragraph, text, **formatting):
        return add_run(paragraph, text, self.settings, **formatting)

    def _render_math(self, paragraph, latex: str, bold: bool = False) -> None:
        """LaTeX-строка → runs с Unicode-символами и sub/sup.

        Это визуализация, не настоящие OMML-формулы. Для MVP — достаточно
        читаемо; полноценный OMML — отдельная задача.
        """
        text = latex_to_unicode(latex.strip().strip("$").strip())
        # Разбиваем на куски: обычный текст / ^{...} / _{...}
        pos = 0
        for match in MATH_TOKEN.finditer(text):
            if match.start() > pos:
                run = self._add_run(paragraph, text[pos:match.start()],
                                    bold=bold, italic=True)
                run.font.name = "Cambria Math"
            token = match.group(0)
            if token.startswith("^"):
                inner = token[2:-1] if token.startswith("^{") else token[1:]
                run = self._add_run(paragraph, inner, bold=bold, italic=True)
                run.font.name = "Cambria Math"
                run.font.superscript = True
            else:
                inner = token[2:-1] if token.startswith("_{") else token[1:]
                run = self._add_run(paragraph, inner, bold=bold, italic=True)
                run.font.name = "Cambria Math"
                run.font.subscript = True
            pos = match.end()
        if pos < len(text):
            run = self._add_run(paragraph, text[pos:], bold=bold, italic=True)
            run.font.name = "Cambria Math"

    def _add_text_with_subsup(self, paragraph, text, bold=False, italic=False) -> None:
        """Разбирает ~X~ и ^X^ (pandoc-расширение), создавая sub/sup runs."""
        pos = 0
        for match in MATH_TOKEN.finditer(text):
            if match.start() > pos:
                self._add_run(paragraph, text[pos:match.start()],
                              bold=bold, italic=italic)
            token = match.group(0)
            if token.startswith("^"):
                inner = token[2:-1] if token.startswith("^{") else token[1:]
                run = self._add_run(paragraph, inner, bold=bold, italic=italic)
                run.font.superscript = True
            else:  # "_"
                inner = token[2:-1] if token.startswith("_{") else token[1:]
                run = self._add_run(paragraph, inner, bold=bold, italic=italic)
                run.font.subscript = True
            pos = match.end()
        if pos < len(text):
            self._add_run(paragraph, text[pos:], bold=bold, italic=italic)

    def _add_list(self, block, list_level: int = 0, num_id=None) -> None:
        ordered = bool(block.get("attrs", {}).get("ordered", False))

        if num_id is None:
            num_id = (
                self.numbering.get_number_num_id() if ordered
                else self.numbering.get_bullet_num_id()
            )

        for item in block.get("children", []):
            for item_block in item.get("children", []):
                item_kind = item_block.get("type")

                if item_kind in ("block_text", "paragraph"):
                    paragraph = self.document.add_paragraph()
                    checked = (
                        item_block.get("attrs", {}).get("checked")
                        if "checked" in item_block.get("attrs", {})
                        else item.get("attrs", {}).get("checked")
                    )
                    if checked is not None:
                        # Чек-лист: свой отступ, маркер — символ ☑/☐
                        paragraph.paragraph_format.left_indent = Cm(0.6 + 0.45 * list_level)
                        paragraph.paragraph_format.first_line_indent = Cm(-0.5)
                        prefix = paragraph.add_run("☑ " if checked else "☐ ")
                        apply_run_format(prefix, self.settings)
                    else:
                        self._apply_numbering(paragraph, num_id, list_level)
                    self._inline_into(paragraph, item_block.get("children", []))

                elif item_kind == "list":
                    self._add_list(item_block, list_level + 1, num_id)

                elif item_kind == "block_code":
                    paragraph = self.document.add_paragraph()
                    self._apply_numbering(paragraph, num_id, list_level)
                    code = clean_xml_string(item_block.get("raw", "").rstrip("\n"))
                    run = self._add_run(paragraph, code)
                    run.font.name = "Consolas"

    def _apply_numbering(self, paragraph, num_id: int, ilvl: int) -> None:
        """Проставляет w:numPr (numId + ilvl) на параграф."""
        pPr = paragraph._element.get_or_add_pPr()
        for existing in pPr.findall(qn("w:numPr")):
            pPr.remove(existing)

        num_pr = OxmlElement("w:numPr")

        ilvl_el = OxmlElement("w:ilvl")
        ilvl_el.set(qn("w:val"), str(ilvl))
        num_pr.append(ilvl_el)

        num_id_el = OxmlElement("w:numId")
        num_id_el.set(qn("w:val"), str(num_id))
        num_pr.append(num_id_el)

        pPr.append(num_pr)

    def _inline_into(self, paragraph, children, base_bold=False, base_italic=False) -> None:
        for child in children or []:
            kind = child.get("type")
            raw = child.get("raw", "")

            if kind == "text":
                self._add_text_with_subsup(
                    paragraph, raw, bold=base_bold, italic=base_italic,
                )
            elif kind == "strong":
                self._inline_into(paragraph, child.get("children", []),
                                  base_bold=True, base_italic=base_italic)
            elif kind == "emphasis":
                self._inline_into(paragraph, child.get("children", []),
                                  base_bold=base_bold, base_italic=True)
            elif kind == "codespan":
                run = self._add_run(paragraph, raw, bold=base_bold, italic=base_italic)
                run.font.name = "Consolas"
            elif kind == "link":
                label = self._plain_text(child.get("children"))
                url = child.get("attrs", {}).get("url", "")
                run = self._add_run(paragraph, f"{label} ({url})" if url else label,
                                    bold=base_bold, italic=base_italic)
                run.underline = True
            elif kind in ("softbreak", "linebreak"):
                paragraph.add_run("\n")
            elif kind == "image":
                alt = self._image_alt(child) or "Изображение"
                self._add_run(paragraph, f"[{alt}]",
                              bold=base_bold, italic=base_italic)
            elif kind == "strikethrough":
                before = len(paragraph.runs)
                self._inline_into(paragraph, child.get("children", []),
                                  base_bold=base_bold, base_italic=base_italic)
                for run in paragraph.runs[before:]:
                    run.font.strike = True
            elif kind == "inline_math":
                self._render_math(paragraph, raw, bold=base_bold)
            else:
                text = self._plain_text([child])
                if text:
                    self._add_run(paragraph, text, bold=base_bold, italic=base_italic)

    # ---------- table ----------

    def _add_table(self, block) -> None:
        header_rows, parsed_rows = [], []
        for section_node in block.get("children", []):
            st = section_node.get("type")
            if st == "table_head":
                header_rows.append([
                    self._plain_text(cell.get("children", []))
                    for cell in section_node.get("children", [])
                ])
            elif st == "table_body":
                for row_node in section_node.get("children", []):
                    if row_node.get("type") == "table_row":
                        parsed_rows.append([
                            self._plain_text(cell.get("children", []))
                            for cell in row_node.get("children", [])
                        ])
            elif st == "table_row":
                parsed_rows.append([
                    self._plain_text(cell.get("children", []))
                    for cell in section_node.get("children", [])
                ])

        all_rows = header_rows + parsed_rows
        if not all_rows:
            return
        column_count = max((len(row) for row in all_rows), default=0)
        if column_count == 0:
            return

        table = self.document.add_table(rows=0, cols=column_count)
        table.style = "Table Grid"
        header_count = len(header_rows)

        for row_index, values in enumerate(all_rows):
            values = values + [""] * (column_count - len(values))
            cells = table.add_row().cells
            for col_index, value in enumerate(values):
                cell = cells[col_index]
                cell.text = ""
                paragraph = cell.paragraphs[0]
                self._add_run(paragraph, value, bold=(row_index < header_count))

                source_row = self._source_row_for(block, row_index, header_count)
                if source_row and col_index < len(source_row):
                    align = source_row[col_index].get("attrs", {}).get("align")
                    paragraph.alignment = {
                        "left": WD_ALIGN_PARAGRAPH.LEFT,
                        "center": WD_ALIGN_PARAGRAPH.CENTER,
                        "right": WD_ALIGN_PARAGRAPH.RIGHT,
                    }.get(align, WD_ALIGN_PARAGRAPH.LEFT)

    def _source_row_for(self, block, row_index, header_count):
        if row_index < header_count:
            for node in block.get("children", []):
                if node.get("type") == "table_head":
                    return node.get("children", [])
            return None
        body_rows = []
        for node in block.get("children", []):
            if node.get("type") == "table_body":
                body_rows = [r for r in node.get("children", [])
                             if r.get("type") == "table_row"]
        body_index = row_index - header_count
        if body_index < len(body_rows):
            return body_rows[body_index].get("children", [])
        return None

    # ---------- blocks ----------

    def _add_blocks(self, blocks, list_level=0) -> None:
        settings, document = self.settings, self.document

        for block in blocks or []:
            kind = block.get("type")
            children = block.get("children", [])

            if kind == "blank_line":
                continue

            if kind == "heading":
                level = int(block.get("attrs", {}).get("level", 1))
                level = min(max(level, 1), 9)
                paragraph = document.add_paragraph(style=f"Heading {level}")
                paragraph.paragraph_format.keep_with_next = True
                paragraph.paragraph_format.space_before = Pt(12 if level == 1 else 8)
                paragraph.paragraph_format.space_after = Pt(5)
                for child in children:
                    if child.get("type") == "text":
                        run = self._add_run(paragraph, child.get("raw", ""), bold=True)
                        apply_run_format(run, settings, heading=True, level=level)
                    else:
                        before = len(paragraph.runs)
                        self._inline_into(paragraph, [child])
                        for run in paragraph.runs[before:]:
                            apply_run_format(run, settings, heading=True, level=level)
                continue

            if kind == "paragraph":
                self._inline_into(document.add_paragraph(), children)

            elif kind == "block_quote":
                start = len(document.paragraphs)
                self._add_blocks(children, list_level)
                for paragraph in document.paragraphs[start:]:
                    paragraph.paragraph_format.left_indent = Cm(0.7)

            elif kind == "list":
                self._add_list(block, list_level=0)

            elif kind == "block_code":
                code = clean_xml_string(block.get("raw", "").rstrip("\n"))
                paragraph = document.add_paragraph()
                paragraph.paragraph_format.left_indent = Cm(0.5)
                paragraph.paragraph_format.space_before = Pt(4)
                paragraph.paragraph_format.space_after = Pt(8)
                run = self._add_run(paragraph, code)
                run.font.name = "Consolas"
                run.font.size = Pt(max(8, float(settings.get("body_size", 12)) - 1))
                run.font.color.rgb = hex_to_rgb("#374151")

            elif kind == "block_math":
                formula = clean_xml_string(block.get("raw", "").strip())
                if formula:
                    paragraph = document.add_paragraph()
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    paragraph.paragraph_format.space_before = Pt(6)
                    paragraph.paragraph_format.space_after = Pt(10)
                    self._render_math(paragraph, formula)

            elif kind == "thematic_break":
                self._add_run(document.add_paragraph(), "─" * 32)

            elif kind == "table":
                self._add_table(block)

            elif kind == "block_html":
                raw = block.get("raw", "").strip()
                if raw:
                    add_inline_regex(document.add_paragraph(), raw, settings)

            else:
                text = self._plain_text(children) or block.get("raw", "")
                if text.strip():
                    add_inline_regex(document.add_paragraph(), text, settings)