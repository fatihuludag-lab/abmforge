from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _clear_scaffold_model_modules() -> None:
    for name in list(sys.modules):
        if name == "model" or name.startswith("model."):
            sys.modules.pop(name, None)


@pytest.fixture(autouse=True)
def _isolate_scaffold_model_modules() -> Iterator[None]:
    """Avoid cross-test import cache leaks between generated study projects."""

    _clear_scaffold_model_modules()
    yield
    _clear_scaffold_model_modules()
