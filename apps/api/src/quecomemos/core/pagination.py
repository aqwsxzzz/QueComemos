"""Offset pagination: the `PageParams` dependency, the `Page[T]` envelope, and
the single helper every list service uses to run a count + a window."""

from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

MAX_PAGE_SIZE = 100


class PageParams:
    """The window a list query should return.

    Built from a feature's FilterParams rather than injected on its own, so the
    whole query string is validated by a single forbid-extras model.
    """

    def __init__(self, page: int = 1, page_size: int = 20) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    has_next: bool


class Page[T](BaseModel):
    data: list[T]
    meta: PageMeta


def build_page[T](items: list[T], total: int, params: PageParams) -> Page[T]:
    return Page(
        data=items,
        meta=PageMeta(
            page=params.page,
            page_size=params.page_size,
            total=total,
            has_next=params.offset + len(items) < total,
        ),
    )


async def paginate[R](
    db: AsyncSession, statement: Select[tuple[R]], params: PageParams
) -> tuple[list[R], int]:
    """Run the count and the windowed query for one already-filtered statement."""
    count_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = (await db.execute(count_statement)).scalar_one()
    windowed = statement.offset(params.offset).limit(params.page_size)
    rows = list((await db.execute(windowed)).scalars().unique().all())
    return rows, total
