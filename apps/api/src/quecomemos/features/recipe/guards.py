"""Cross-entity assertions for recipes."""

from quecomemos.core.errors import ForbiddenError
from quecomemos.features.recipe.models import Recipe
from quecomemos.features.user.models import User


def assert_can_edit(recipe: Recipe, user: User) -> None:
    """Authors edit their own recipes; maintainers can act on any of them."""
    if recipe.author_id == user.id or user.is_maintainer:
        return
    raise ForbiddenError("Esta receta no es tuya")
