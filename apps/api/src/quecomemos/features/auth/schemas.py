"""Auth request/response bodies."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from quecomemos.features.user.schemas import UserRead


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str


class TokenPair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthSession(BaseModel):
    """What login and register return: who you are, plus how to prove it."""

    model_config = ConfigDict(extra="forbid")

    user: UserRead
    tokens: TokenPair
