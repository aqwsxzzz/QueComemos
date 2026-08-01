"""The parser must never fail a write — worst case it extracts nothing."""

import pytest

from quecomemos.features.recipe.parser import parse_ingredient_line
from quecomemos.features.recipe.units import Unit


@pytest.mark.parametrize(
    ("line", "quantity", "unit", "name"),
    [
        ("2 tazas de harina", 2.0, Unit.TAZA, "harina"),
        ("500 g de carne picada", 500.0, Unit.GRAMO, "carne picada"),
        ("1 kg de papas", 1.0, Unit.KILOGRAMO, "papas"),
        ("3 dientes de ajo", 3.0, Unit.DIENTE, "ajo"),
        ("1,5 l de leche", 1.5, Unit.LITRO, "leche"),
        ("1/2 taza de azucar", 0.5, Unit.TAZA, "azucar"),
        ("2 cdas de aceite de oliva", 2.0, Unit.CUCHARADA, "aceite de oliva"),
        ("½ cebolla", 0.5, None, "cebolla"),
        ("2 tomates", 2.0, None, "tomates"),
    ],
)
def test_parses_quantity_unit_and_name(
    line: str, quantity: float, unit: Unit | None, name: str
) -> None:
    parsed = parse_ingredient_line(line)

    assert parsed.quantity == quantity
    assert parsed.unit == unit
    assert parsed.name == name


def test_a_range_takes_the_low_end() -> None:
    parsed = parse_ingredient_line("2-3 zanahorias")

    assert parsed.quantity == 2.0
    assert parsed.name == "zanahorias"


def test_to_taste_becomes_a_unit_and_leaves_a_matchable_name() -> None:
    parsed = parse_ingredient_line("sal a gusto")

    assert parsed.unit == Unit.AL_GUSTO
    assert parsed.quantity is None
    assert parsed.name == "sal"


def test_unparseable_line_keeps_the_whole_text_as_the_name() -> None:
    parsed = parse_ingredient_line("tomate cherry del huerto de mi abuela")

    assert parsed.quantity is None
    assert parsed.unit is None
    assert parsed.name == "tomate cherry del huerto de mi abuela"


def test_parsing_never_raises_on_odd_input() -> None:
    for line in ["", "   ", "1/0 taza", "0 g", "///", "12345678901234567890 g"]:
        parse_ingredient_line(line)
