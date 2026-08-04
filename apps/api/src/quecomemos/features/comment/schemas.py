"""Comment shapes.

A "help me out" question is not a separate entity: it is a comment with
kind='question' and the step it asks about. See PRODUCT.md.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from quecomemos.core.filters import FilterParams
from quecomemos.features.comment.models import CommentKind
from quecomemos.features.user.schemas import CookRead


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(min_length=1, max_length=2000)
    kind: CommentKind = CommentKind.COMMENT
    step_id: uuid.UUID | None = None


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    body: str
    kind: CommentKind
    step_id: uuid.UUID | None
    created_at: datetime
    author: CookRead


class CommentFilters(FilterParams):
    kind: CommentKind | None = None
    step_id: uuid.UUID | None = None
