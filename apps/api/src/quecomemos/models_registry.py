"""Single import point for every SQLAlchemy model.

Alembic autogenerate only sees tables whose modules have been imported. Feature
model modules are registered here so no feature has to know about migrations.
"""

import importlib

FEATURE_MODEL_MODULES: tuple[str, ...] = ()


def import_all_models() -> None:
    for module in FEATURE_MODEL_MODULES:
        importlib.import_module(module)
