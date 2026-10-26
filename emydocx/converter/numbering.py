"""Собственные определения нумерации для маркированных и нумерованных списков.

Встроенный шаблон python-docx для стилей "List Bullet 2/3" часто переиспользует
один и тот же маркер •. Здесь мы создаём свои abstractNum/num с разными
маркерами по уровням (повторяются до предельных 9 уровней DOCX):
    Bullets: ●, ○, ■
    Numbers: 1., a., i.
"""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class NumberingManager:
    def __init__(self, document):
        self.document = document
        self.numbering = document.part.numbering_part.element
        self._bullet_abstract_id = None
        self._number_abstract_id = None
        self._next_num_id = None

    # ---------- public ----------

    def get_bullet_num_id(self) -> int:
        if self._bullet_abstract_id is None:
            self._bullet_abstract_id = self._next_abstract_id()
            abstract = self._create_bullet_abstract(self._bullet_abstract_id)
            self._insert_abstract(abstract)
        return self._create_num(self._bullet_abstract_id)

    def get_number_num_id(self) -> int:
        if self._number_abstract_id is None:
            self._number_abstract_id = self._next_abstract_id()
            abstract = self._create_number_abstract(self._number_abstract_id)
            self._insert_abstract(abstract)
        return self._create_num(self._number_abstract_id)

    # ---------- ids ----------

    def _next_abstract_id(self) -> int:
        existing = [
            int(el.get(qn("w:abstractNumId")))
            for el in self.numbering.findall(qn("w:abstractNum"))
        ]
        return max(existing) + 1 if existing else 0

    def _next_num_id_value(self) -> int:
        if self._next_num_id is None:
            existing = [
                int(el.get(qn("w:numId")))
                for el in self.numbering.findall(qn("w:num"))
            ]
            self._next_num_id = max(existing) + 1 if existing else 1
        else:
            self._next_num_id += 1
        return self._next_num_id

    def _insert_abstract(self, abstract) -> None:
        """w:abstractNum должны идти перед всеми w:num (требование схемы)."""
        first_num = self.numbering.find(qn("w:num"))
        if first_num is not None:
            first_num.addprevious(abstract)
        else:
            self.numbering.append(abstract)

    def _create_num(self, abstract_id: int) -> int:
        num_id = self._next_num_id_value()
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(num_id))
        abstract_ref = OxmlElement("w:abstractNumId")
        abstract_ref.set(qn("w:val"), str(abstract_id))
        num.append(abstract_ref)
        self.numbering.append(num)
        return num_id

    # ---------- abstract defs ----------

    def _create_bullet_abstract(self, abstract_id: int):
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(abstract_id))

        multi = OxmlElement("w:multiLevelType")
        multi.set(qn("w:val"), "hybridMultilevel")
        abstract.append(multi)

        # Точные Unicode-символы, которые использует Google Docs и современный Word
        bullet_chars = ["\u25CF", "\u25CB", "\u25A0"]  # ● ○ ■

        for ilvl in range(9):
            char = bullet_chars[ilvl % len(bullet_chars)]
            lvl = OxmlElement("w:lvl")
            lvl.set(qn("w:ilvl"), str(ilvl))

            start = OxmlElement("w:start")
            start.set(qn("w:val"), "1")
            lvl.append(start)

            fmt = OxmlElement("w:numFmt")
            fmt.set(qn("w:val"), "bullet")
            lvl.append(fmt)

            text = OxmlElement("w:lvlText")
            text.set(qn("w:val"), char)
            lvl.append(text)

            jc = OxmlElement("w:lvlJc")
            jc.set(qn("w:val"), "left")
            lvl.append(jc)

            pPr = OxmlElement("w:pPr")
            ind = OxmlElement("w:ind")
            # Точные отступы как в Google Docs (720 twips = 0.5 дюйма)
            ind.set(qn("w:left"), str(720 + ilvl * 720))
            ind.set(qn("w:hanging"), "360")
            pPr.append(ind)
            lvl.append(pPr)

            # Убираем подчеркивание (как в Google Docs), rFonts НЕ указываем
            rPr = OxmlElement("w:rPr")
            u = OxmlElement("w:u")
            u.set(qn("w:val"), "none")
            rPr.append(u)
            lvl.append(rPr)

            abstract.append(lvl)

        return abstract


    def _create_number_abstract(self, abstract_id: int):
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(abstract_id))

        multi = OxmlElement("w:multiLevelType")
        multi.set(qn("w:val"), "hybridMultilevel")
        abstract.append(multi)

        formats = ["decimal", "lowerLetter", "lowerRoman"]
        for ilvl in range(9):
            lvl = OxmlElement("w:lvl")
            lvl.set(qn("w:ilvl"), str(ilvl))

            start = OxmlElement("w:start")
            start.set(qn("w:val"), "1")
            lvl.append(start)

            fmt = OxmlElement("w:numFmt")
            fmt.set(qn("w:val"), formats[ilvl % len(formats)])
            lvl.append(fmt)

            text = OxmlElement("w:lvlText")
            text.set(qn("w:val"), f"%{ilvl + 1}.")
            lvl.append(text)

            jc = OxmlElement("w:lvlJc")
            jc.set(qn("w:val"), "left")
            lvl.append(jc)

            pPr = OxmlElement("w:pPr")
            ind = OxmlElement("w:ind")
            ind.set(qn("w:left"), str(720 + ilvl * 720))
            ind.set(qn("w:hanging"), "360")
            pPr.append(ind)
            lvl.append(pPr)

            abstract.append(lvl)

        return abstract
