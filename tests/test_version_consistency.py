from __future__ import annotations

import re
from pathlib import Path

import abmforge
from abmforge import Model, Scenario

ROOT = Path(__file__).resolve().parents[1]


def _read_pyproject_version() -> str:
    pyproject = ROOT / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    assert match is not None, "Could not find project version in pyproject.toml"
    return match.group(1)


class EmptyModel(Model):
    """Minimal model used for version metadata tests."""


def test_imported_version_matches_pyproject() -> None:
    assert abmforge.__version__ == _read_pyproject_version()


def test_scenario_records_current_abmforge_version() -> None:
    scenario = Scenario(model=EmptyModel, seed=123, steps=0, name="version-test")

    result = scenario.run()

    assert result.dataset.runs
    assert result.dataset.runs[-1]["abmforge_version"] == abmforge.__version__
