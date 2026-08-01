"""Shared list-query plumbing: the filter base every feature extends, plus a
whitelisted sort applier. Sorting outside the whitelist is a 422, never a 500."""

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute

from quecomemos.core.errors import ValidationError

SortableColumns = Mapping[str, InstrumentedAttribute[object]]


class FilterParams(BaseModel):
    """Base for feature filter schemas. Unknown query params are rejected."""

    model_config = ConfigDict(extra="forbid")

    q: str | None = None
    sort: str | None = None


def apply_sort[R](
    statement: Select[tuple[R]],
    sortable: SortableColumns,
    sort: str | None,
    default: str,
) -> Select[tuple[R]]:
    """`sort=title` ascending, `sort=-published_at` descending."""
    raw = (sort or default).strip()
    descending = raw.startswith("-")
    key = raw[1:] if descending else raw

    column = sortable.get(key)
    if column is None:
        allowed = ", ".join(sorted(sortable))
        raise ValidationError(f"Orden inválido: '{key}'. Opciones: {allowed}")

    return statement.order_by(column.desc() if descending else column.asc())
