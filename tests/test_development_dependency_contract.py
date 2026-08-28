from __future__ import annotations

import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]

OPTIONAL_SURFACES = ("data", "analysis", "viz", "docs")
VALIDATION_WORKFLOWS = (
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".github" / "workflows" / "release.yml",
)


def _optional_dependencies() -> dict[str, list[str]]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["optional-dependencies"]


def _requirement_name(requirement: str) -> str:
    match = re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*", requirement)
    assert match is not None, requirement
    return match.group(0).lower().replace("_", "-").replace(".", "-")


def test_dev_extra_covers_all_validation_optional_surfaces() -> None:
    extras = _optional_dependencies()
    dev = set(extras["dev"])

    required = set().union(*(set(extras[name]) for name in OPTIONAL_SURFACES))

    missing = sorted(required - dev)

    assert not missing, f"dev extra is missing validation dependencies: {missing}"


def test_dev_extra_has_no_duplicate_distribution_names() -> None:
    extras = _optional_dependencies()
    names = [_requirement_name(item) for item in extras["dev"]]

    duplicates = sorted(name for name in set(names) if names.count(name) > 1)

    assert not duplicates, f"duplicate dev dependencies: {duplicates}"


def test_ci_and_release_use_single_dev_validation_contract() -> None:
    expected = 'python -m pip install -e ".[dev]"'
    legacy = ".[dev,data,viz,analysis,docs]"

    for workflow_path in VALIDATION_WORKFLOWS:
        workflow = workflow_path.read_text(encoding="utf-8")

        assert expected in workflow, workflow_path
        assert legacy not in workflow, workflow_path


def test_documented_validation_workflows_use_dev_contract() -> None:
    legacy = ".[dev,data,viz,analysis,docs]"
    expected = ".[dev]"

    documents = (
        ROOT / "CONTRIBUTING.md",
        ROOT / "README.md",
        ROOT / "docs" / "contributing.md",
        ROOT / "docs" / "getting-started.md",
        ROOT / "docs" / "researcher-quickstart.md",
        ROOT / "docs" / "reference-reproducible-workflow.md",
        ROOT / "docs" / "reproducibility-tiers.md",
    )

    for document in documents:
        content = document.read_text(encoding="utf-8")

        assert expected in content, document
        assert legacy not in content, document


def test_user_facing_install_docs_include_data_extra() -> None:
    documents = (
        ROOT / "README.md",
        ROOT / "docs" / "getting-started.md",
    )

    for document in documents:
        content = document.read_text(encoding="utf-8")

        assert ".[data]" in content, document
