"""Минимальная LaTeX → Unicode конверсия для DOCX MVP.

Полноценные формулы требуют OMML (Office Math Markup). Здесь только
частые символы и операторы: греческий алфавит, интегралы, суммы,
акценты, простые дроби. Всё, что не распознано — остаётся как есть.
"""
import re

_SYMBOLS = {
    # Греческий (нижний регистр)
    "\\alpha": "α", "\\beta": "β", "\\gamma": "γ", "\\delta": "δ",
    "\\epsilon": "ε", "\\varepsilon": "ε", "\\zeta": "ζ", "\\eta": "η",
    "\\theta": "θ", "\\vartheta": "ϑ", "\\iota": "ι", "\\kappa": "κ",
    "\\lambda": "λ", "\\mu": "μ", "\\nu": "ν", "\\xi": "ξ",
    "\\pi": "π", "\\rho": "ρ", "\\sigma": "σ", "\\tau": "τ",
    "\\upsilon": "υ", "\\phi": "φ", "\\varphi": "φ", "\\chi": "χ",
    "\\psi": "ψ", "\\omega": "ω",
    # Греческий (верхний регистр)
    "\\Gamma": "Γ", "\\Delta": "Δ", "\\Theta": "Θ", "\\Lambda": "Λ",
    "\\Xi": "Ξ", "\\Pi": "Π", "\\Sigma": "Σ", "\\Phi": "Φ",
    "\\Psi": "Ψ", "\\Omega": "Ω",
    # Операторы и множества
    "\\int": "∫", "\\iint": "∬", "\\iiint": "∭",
    "\\sum": "∑", "\\prod": "∏", "\\coprod": "∐",
    "\\infty": "∞", "\\partial": "∂", "\\nabla": "∇",
    "\\pm": "±", "\\mp": "∓", "\\times": "×", "\\div": "÷",
    "\\cdot": "·", "\\ast": "∗", "\\star": "⋆",
    "\\ldots": "…", "\\cdots": "⋯", "\\vdots": "⋮",
    "\\to": "→", "\\rightarrow": "→", "\\leftarrow": "←",
    "\\Rightarrow": "⇒", "\\Leftarrow": "⇐", "\\leftrightarrow": "↔",
    "\\le": "≤", "\\leq": "≤", "\\ge": "≥", "\\geq": "≥",
    "\\ne": "≠", "\\neq": "≠", "\\approx": "≈", "\\equiv": "≡",
    "\\sim": "∼", "\\propto": "∝",
    "\\in": "∈", "\\notin": "∉", "\\ni": "∋",
    "\\subset": "⊂", "\\subseteq": "⊆", "\\supset": "⊃",
    "\\supseteq": "⊇", "\\cup": "∪", "\\cap": "∩",
    "\\emptyset": "∅", "\\varnothing": "∅",
    "\\forall": "∀", "\\exists": "∃", "\\nexists": "∄",
    "\\wedge": "∧", "\\vee": "∨", "\\neg": "¬",
    "\\sqrt": "√", "\\angle": "∠", "\\perp": "⊥", "\\parallel": "∥",
    "\\langle": "⟨", "\\rangle": "⟩",
    "\\lfloor": "⌊", "\\rfloor": "⌋", "\\lceil": "⌈", "\\rceil": "⌉",
    # Акценты (combining)
    "\\hat": "\u0302", "\\bar": "\u0304", "\\vec": "\u20D7",
    "\\dot": "\u0307", "\\ddot": "\u0308", "\\tilde": "\u0303",
    # Пробелы
    "\\,": " ", "\\;": " ", "\\:": " ", "\\ ": " ",
    "\\quad": "  ", "\\qquad": "    ",
    "\\!": "",
}

#: \command{arg} — сначала аргументные команды, потом простые символы.
_ARG_PATTERN = re.compile(r"\\(hat|bar|vec|dot|ddot|tilde)\{([^{}]*)\}")
_CMD_PATTERN = re.compile(r"\\[A-Za-z]+")


def _apply_arg_commands(text: str) -> str:
    def repl(m):
        cmd, arg = m.group(1), m.group(2)
        accent = _SYMBOLS.get(f"\\{cmd}", "")
        return (arg + accent) if arg else ""
    return _ARG_PATTERN.sub(repl, text)


def _replace_symbols(text: str) -> str:
    def repl(m):
        return _SYMBOLS.get(m.group(0), m.group(0))
    return _CMD_PATTERN.sub(repl, text)


def latex_to_unicode(expr: str) -> str:
    """Конвертирует базовый LaTeX в Unicode; неизвестные команды оставляет."""
    if not expr:
        return ""
    expr = _apply_arg_commands(expr)
    expr = _replace_symbols(expr)
    # Убираем оставшиеся одинарные фигурные скобки-группировки: {x} → x
    expr = re.sub(r"\{([^{}]*)\}", r"\1", expr)
    return expr


#: Разбиение по ^{...}, _{...}, ^X, _X — для создания sup/sub runs.
MATH_TOKEN = re.compile(r"(\^\{[^{}]*\}|\^[A-Za-z0-9]|_\{[^{}]*\}|_[A-Za-z0-9])")