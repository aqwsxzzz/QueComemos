"""Serialization for accounts. `password_hash` is never exposed."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=60)


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, min_length=2, max_length=60)
    bio: str | None = Field(default=None, max_length=280)


class UserRead(BaseModel):
    """The account as its owner sees it."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    email: EmailStr
    display_name: str
    bio: str | None
    is_maintainer: bool
    created_at: datetime


class CookRead(BaseModel):
    """A cook as everyone else sees them. No email, ever."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    display_name: str
    bio: str | None
    created_at: datetime
