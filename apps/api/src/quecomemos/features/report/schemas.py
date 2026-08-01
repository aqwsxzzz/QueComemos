"""Moderation request/response shapes."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from quecomemos.core.filters import FilterParams
from quecomemos.features.report.models import ReportReason, ReportStatus, ReportTarget


class ReportCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_type: ReportTarget
    target_id: uuid.UUID
    reason: ReportReason
    note: str | None = Field(default=None, max_length=1000)


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    target_type: ReportTarget
    target_id: uuid.UUID
    reason: ReportReason
    note: str | None
    status: ReportStatus
    created_at: datetime


class ReportResolve(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ReportStatus


class ReportFilters(FilterParams):
    status: ReportStatus | None = None
    target_type: ReportTarget | None = None


class BlockCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blocked_id: uuid.UUID


class BlockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    blocked_id: uuid.UUID
    created_at: datetime
