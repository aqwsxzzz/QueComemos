"""Free-text search over a feature-declared column whitelist.

Deliberately ILIKE-based for phase A. When the pool grows past what this can
serve, the replacement is a Postgres tsvector column — not client-side filtering.
"""

from collections.abc import Sequence

from sqlalchemy import ColumnElement, Select, or_
from sqlalchemy.orm import InstrumentedAttribute


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_clause(
    columns: Sequence[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]],
    term: str,
) -> ColumnElement[bool] | None:
    """Builds `col ILIKE %term%` OR-ed across the whitelisted columns."""
    cleaned = term.strip()
    if not cleaned or not columns:
        return None
    pattern = f"%{_escape_like(cleaned)}%"
    return or_(*(column.ilike(pattern, escape="\\") for column in columns))


def apply_search[R](
    statement: Select[tuple[R]],
    columns: Sequence[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]],
    term: str | None,
) -> Select[tuple[R]]:
    if term is None:
        return statement
    clause = search_clause(columns, term)
    return statement if clause is None else statement.where(clause)
