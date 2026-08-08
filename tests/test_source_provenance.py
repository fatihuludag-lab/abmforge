from __future__ import annotations

import hashlib
import importlib
import subprocess
import sys
from pathlib import Path

import pytest

from abmforge import Model
from abmforge.repro import SourceRepositoryProvenanceV1


def _init_repository(
    path: Path,
    *,
    filename: str,
    content: str,
) -> str:
    path.mkdir()
    (path / filename).write_text(content, encoding="utf-8")
    (path / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@example.com"],
        cwd=path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "ABMForge Tests"],
        cwd=path,
        check=True,
    )
    subprocess.run(["git", "add", filename, ".gitignore"], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial"],
        cwd=path,
        check=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_source_provenance_uses_model_repository_not_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_repo = tmp_path / "source-repo"
    source_commit = _init_repository(
        source_repo,
        filename="source_model.py",
        content=("from abmforge import Model\n\nclass SourceRepositoryModel(Model):\n    pass\n"),
    )
    working_repo = tmp_path / "working-repo"
    _init_repository(
        working_repo,
        filename="README.md",
        content="unrelated working repository\n",
    )

    sys.path.insert(0, str(source_repo))
    try:
        source_module = importlib.import_module("source_model")
        monkeypatch.chdir(working_repo)

        provenance = SourceRepositoryProvenanceV1.from_model(source_module.SourceRepositoryModel)
    finally:
        sys.path.remove(str(source_repo))
        sys.modules.pop("source_model", None)

    assert provenance.repository_available is True
    assert provenance.commit == source_commit
    assert provenance.source_path == "source_model.py"
    assert provenance.dirty is False


def test_source_provenance_hashes_model_source_and_detects_dirty_tree(
    tmp_path: Path,
) -> None:
    source_repo = tmp_path / "source-repo"
    _init_repository(
        source_repo,
        filename="source_model.py",
        content=("from abmforge import Model\n\nclass SourceRepositoryModel(Model):\n    pass\n"),
    )

    sys.path.insert(0, str(source_repo))
    try:
        source_module = importlib.import_module("source_model")
        model = source_module.SourceRepositoryModel
        clean = SourceRepositoryProvenanceV1.from_model(model)

        source_path = source_repo / "source_model.py"
        source_path.write_text(
            source_path.read_text(encoding="utf-8") + "\nDIRTY = True\n",
            encoding="utf-8",
        )
        dirty = SourceRepositoryProvenanceV1.from_model(model)
    finally:
        sys.path.remove(str(source_repo))
        sys.modules.pop("source_model", None)

    expected_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    assert clean.dirty is False
    assert dirty.dirty is True
    assert clean.source_sha256 != dirty.source_sha256
    assert dirty.source_sha256 == expected_sha256


def test_source_provenance_records_non_git_source_without_using_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    module_path = source_dir / "standalone_model.py"
    module_path.write_text(
        "from abmforge import Model\n\nclass StandaloneModel(Model):\n    pass\n",
        encoding="utf-8",
    )

    unrelated_repo = tmp_path / "unrelated-repo"
    _init_repository(
        unrelated_repo,
        filename="README.md",
        content="unrelated repository\n",
    )

    sys.path.insert(0, str(source_dir))
    try:
        module = importlib.import_module("standalone_model")
        monkeypatch.chdir(unrelated_repo)
        provenance = SourceRepositoryProvenanceV1.from_model(module.StandaloneModel)
    finally:
        sys.path.remove(str(source_dir))
        sys.modules.pop("standalone_model", None)

    assert provenance.source_available is True
    assert provenance.source_path == "standalone_model.py"
    assert provenance.source_sha256 is not None
    assert provenance.repository_available is False
    assert provenance.commit is None


def test_source_provenance_is_fail_closed_when_source_is_unavailable() -> None:
    dynamic_model = type(
        "DynamicModel",
        (Model,),
        {"__module__": "module_that_does_not_exist"},
    )

    provenance = SourceRepositoryProvenanceV1.from_model(dynamic_model)

    assert provenance.source_available is False
    assert provenance.source_path is None
    assert provenance.source_sha256 is None
    assert provenance.repository_available is False


def test_source_provenance_to_dict_has_versioned_model_scope(tmp_path: Path) -> None:
    source_repo = tmp_path / "source-repo"
    source_commit = _init_repository(
        source_repo,
        filename="source_model.py",
        content=("from abmforge import Model\n\nclass SourceRepositoryModel(Model):\n    pass\n"),
    )

    sys.path.insert(0, str(source_repo))
    try:
        module = importlib.import_module("source_model")
        payload = SourceRepositoryProvenanceV1.from_model(module.SourceRepositoryModel).to_dict()
    finally:
        sys.path.remove(str(source_repo))
        sys.modules.pop("source_model", None)

    assert payload["schema_version"] == "source-repository-provenance-v1"
    assert payload["scope"] == "model-source"
    assert payload["available"] is True
    assert payload["commit"] == source_commit
    assert payload["source_path"] == "source_model.py"
    assert payload["source_sha256"]
