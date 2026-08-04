"""Text normalization for ingredient matching.

Load-bearing rule from docs/ingredients-model.md: this normalizes **for matching
only**. `recipe_ingredient.raw_text` is never passed through here on the way to
storage — it is stored and displayed exactly as the author typed it.

Spanish plurals are ambiguous in a way that matters here: `tomates` is
`tomate` + s, but `limones` is `limón` + es. A single rule cannot produce the
same key for both pairs, so matching generates a small set of candidate keys
instead of guessing once. Aliases are stored under the conservative key; lookup
tries the conservative key first and the stronger one only as a fallback.
"""

import re
import unicodedata

_WHITESPACE = re.compile(r"\s+")
_NON_WORD = re.compile(r"[^\w\s-]", flags=re.UNICODE)


def strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def normalize(value: str) -> str:
    """lowercase → strip accents → drop punctuation → collapse whitespace."""
    lowered = strip_accents(value.lower())
    cleaned = _NON_WORD.sub(" ", lowered)
    return _WHITESPACE.sub(" ", cleaned).strip()


def singularize(word: str) -> str:
    """Conservative Spanish singular: drops a trailing `s` only.

    `tomates` → `tomate`, `papas` → `papa`. Leaves `limones` alone, which the
    strong form below handles.
    """
    if len(word) <= 3:
        return word
    if word.endswith("ces"):
        return f"{word[:-3]}z"
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def singularize_strong(word: str) -> str:
    """Drops a trailing `es`: `limones` → `limon`, `panes` → `pan`.

    Only ever used as a fallback candidate, never to write an alias.
    """
    if len(word) <= 4:
        return singularize(word)
    if word.endswith("ces"):
        return f"{word[:-3]}z"
    if word.endswith("es"):
        return word[:-2]
    return singularize(word)


def normalize_for_match(value: str) -> str:
    """The canonical matching key. This is what `ingredient_alias` stores."""
    return " ".join(singularize(word) for word in normalize(value).split())


def match_candidates(value: str) -> list[str]:
    """Keys to try against `ingredient_alias`, most-likely first.

    Ordered and de-duplicated, so a caller can `WHERE normalized IN (...)` and
    still know which hit to prefer.
    """
    words = normalize(value).split()
    candidates = [
        " ".join(singularize(word) for word in words),
        " ".join(singularize_strong(word) for word in words),
    ]
    seen: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.append(candidate)
    return seen
