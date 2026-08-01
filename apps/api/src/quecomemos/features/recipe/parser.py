"""Split a free-text ingredient line into quantity, unit and ingredient name.

Nothing here can fail a write. Whatever cannot be parsed is left out of the
structured columns, and `raw_text` still carries exactly what the author typed.
"""

import re
from dataclasses import dataclass
from fractions import Fraction

from quecomemos.core.text import normalize
from quecomemos.features.recipe.units import TO_TASTE_PHRASES, UNIT_SYNONYMS, Unit

_VULGAR_FRACTIONS = {
    "½": Fraction(1, 2),
    "⅓": Fraction(1, 3),
    "⅔": Fraction(2, 3),
    "¼": Fraction(1, 4),
    "¾": Fraction(3, 4),
    "⅛": Fraction(1, 8),
}

# – is the en dash: a range gets typed as "2-3", "2 a 3", or with a real dash.
_LEADING_QUANTITY = re.compile(
    "^\\s*"
    "(?P<whole>\\d+(?:[.,]\\d+)?)"  # 2  |  1,5
    "(?:\\s*[-–a]\\s*\\d+(?:[.,]\\d+)?)?"  # optional range: take the low end
    "(?:\\s*/\\s*(?P<denominator>\\d+))?"  # 1/2
    "\\s*"
)

_DE_PREFIX = re.compile(r"^\s*de\s+", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class ParsedIngredient:
    quantity: float | None
    unit: Unit | None
    name: str


def _parse_vulgar_fraction(text: str) -> tuple[float | None, str]:
    stripped = text.lstrip()
    if stripped and stripped[0] in _VULGAR_FRACTIONS:
        return float(_VULGAR_FRACTIONS[stripped[0]]), stripped[1:]
    return None, text


def _parse_quantity(text: str) -> tuple[float | None, str]:
    quantity, remainder = _parse_vulgar_fraction(text)
    if quantity is not None:
        return quantity, remainder

    match = _LEADING_QUANTITY.match(text)
    if match is None:
        return None, text

    whole = float(match.group("whole").replace(",", "."))
    denominator = match.group("denominator")
    if denominator is not None and float(denominator) != 0:
        whole = whole / float(denominator)
    return whole, text[match.end() :]


def _parse_unit(text: str) -> tuple[Unit | None, str]:
    words = text.split()
    if not words:
        return None, text
    unit = UNIT_SYNONYMS.get(normalize(words[0]))
    if unit is None:
        return None, text
    return unit, " ".join(words[1:])


def _strip_to_taste(text: str) -> tuple[bool, str]:
    """`"sal a gusto"` → `(True, "sal")`, so the name still matches an alias."""
    normalized = normalize(text)
    for phrase in TO_TASTE_PHRASES:
        if phrase in normalized:
            return True, normalized.replace(phrase, "").strip(" ,.;:-")
    return False, text


def parse_ingredient_line(raw_text: str) -> ParsedIngredient:
    """`"2 tazas de harina"` → `(2.0, TAZA, "harina")`.

    The name is what gets matched against the alias table: feeding it the whole
    line would mean `"2 tomates"` never matches the alias `tomate`.
    """
    quantity, remainder = _parse_quantity(raw_text)
    unit, remainder = _parse_unit(remainder)
    name = _DE_PREFIX.sub("", remainder).strip(" ,.;:-")

    if unit is None and quantity is None:
        to_taste, without_phrase = _strip_to_taste(name)
        if to_taste:
            return ParsedIngredient(quantity=None, unit=Unit.AL_GUSTO, name=without_phrase)

    return ParsedIngredient(quantity=quantity, unit=unit, name=name or raw_text.strip())
