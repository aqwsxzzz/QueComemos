"""Follow request/response shapes."""

from quecomemos.core.filters import FilterParams
from quecomemos.features.user.schemas import CookRead


class FollowStatus(CookRead):
    """A cook, plus whether the current user follows them."""

    is_followed: bool


class CookFilters(FilterParams):
    """`q` searches display names; sort is whitelisted in the service."""
