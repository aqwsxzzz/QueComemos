"""Single import point for every SQLAlchemy model.

Alembic autogenerate only sees tables whose modules have been imported. Feature
model modules are registered here so no feature has to know about migrations.
"""

import importlib

FEATURE_MODEL_MODULES: tuple[str, ...] = (
    "quecomemos.features.user.models",
    "quecomemos.features.ingredient.models",
    "quecomemos.features.recipe.models",
    "quecomemos.features.photo.models",
    "quecomemos.features.follow.models",
    "quecomemos.features.favorite.models",
    "quecomemos.features.comment.models",
    "quecomemos.features.report.models",
)


def import_all_models() -> None:
    for module in FEATURE_MODEL_MODULES:
        importlib.import_module(module)
