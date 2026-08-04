"""Shared list-query plumbing: the filter base every feature extends, plus a
whitelisted sort applier. Sorting outside the whitelist is a 422, never a 500."""

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute

from quecomemos.core.errors import ValidationError
from quecomemos.core.pagination import MAX_PAGE_SIZE, PageParams

SortableColumns = Mapping[str, InstrumentedAttribute[object]]


class FilterParams(BaseModel):
    """Base for feature filter schemas.

    Pagination lives here rather than in a second dependency because FastAPI
    validates the whole query string against this model: with `extra="forbid"`,
    any key declared elsewhere would be rejected as unknown.
    """

    model_config = ConfigDict(extra="forbid")

    q: str | None = None
    sort: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=MAX_PAGE_SIZE)

    @property
    def page_params(self) -> PageParams:
        return PageParams(page=self.page, page_size=self.page_size)


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
