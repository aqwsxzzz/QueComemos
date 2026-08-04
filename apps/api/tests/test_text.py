"""Normalization is matching-only. These cases guard the regional vocabulary."""

import pytest

from quecomemos.core.text import (
    match_candidates,
    normalize,
    normalize_for_match,
    singularize,
    singularize_strong,
    strip_accents,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Piña", "pina"),
        ("MAÍZ", "maiz"),
        ("Jalapeño", "jalapeno"),
        ("  cebolla   de  verdeo ", "cebolla de verdeo"),
        ("tomate, cherry", "tomate cherry"),
    ],
)
def test_normalize_lowercases_and_strips(raw: str, expected: str) -> None:
    assert normalize(raw) == expected


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("tomates", "tomate"),
        ("lentejas", "lenteja"),
        ("nueces", "nuez"),
        ("papas", "papa"),
        ("arroz", "arroz"),
        ("pan", "pan"),
        # Short words are left alone: over-stripping them causes false matches.
        ("mes", "mes"),
    ],
)
def test_singularize_drops_only_trailing_s(word: str, expected: str) -> None:
    assert singularize(word) == expected


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("limones", "limon"),
        ("panes", "pan"),
        ("nueces", "nuez"),
        ("tomates", "tomat"),
    ],
)
def test_singularize_strong_drops_es(word: str, expected: str) -> None:
    assert singularize_strong(word) == expected


def test_normalize_for_match_combines_both_passes() -> None:
    assert normalize_for_match("2 Tomates Perita") == "2 tomate perita"


def test_candidates_cover_both_plural_shapes() -> None:
    # The conservative key wins for -s plurals...
    assert "tomate" in match_candidates("Tomates")
    # ...and the strong key rescues -es plurals, whose alias is stored singular.
    assert "limon" in match_candidates("Limones")


def test_candidates_are_ordered_and_deduplicated() -> None:
    assert match_candidates("cebolla") == ["cebolla"]


def test_strip_accents_preserves_letters() -> None:
    assert strip_accents("ñandú") == "nandu"


def test_normalization_never_mutates_input() -> None:
    raw = "Tomate cherry orgánico del huerto de mi abuela"

    normalize_for_match(raw)

    assert raw == "Tomate cherry orgánico del huerto de mi abuela"
