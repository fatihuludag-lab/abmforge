from __future__ import annotations

import subprocess
from pathlib import Path

from abmforge.repro import (
    FRAMEWORK_PROVENANCE_SCHEMA_VERSION,
    FrameworkProvenanceV1,
)


def _init_framework_repository(root: Path) -> tuple[Path, str]:
    package_root = root / "src" / "abmforge"
    package_root.mkdir(parents=True)

    (package_root / "__init__.py").write_text(
        '__version__ = "9.9.9"\n',
        encoding="utf-8",
    )
    (package_root / "core.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    (root / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n",
        encoding="utf-8",
    )

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@example.com"],
        cwd=root,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "ABMForge Tests"],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial"],
        cwd=root,
        check=True,
    )
    subprocess.run(
        [
            "git",
            "remote",
            "add",
            "origin",
            "https://github.com/example/abmforge.git",
        ],
        cwd=root,
        check=True,
    )

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    return package_root, commit


def test_framework_provenance_records_source_checkout(
    tmp_path: Path,
) -> None:
    package_root, commit = _init_framework_repository(tmp_path / "framework-repo")

    provenance = FrameworkProvenanceV1.from_package_root(
        package_root,
        version="9.9.9",
    )

    assert provenance.schema_version == FRAMEWORK_PROVENANCE_SCHEMA_VERSION
    assert provenance.scope == "abmforge-framework"
    assert provenance.name == "abmforge"
    assert provenance.version == "9.9.9"
    assert provenance.install_mode == "source-checkout"

    assert provenance.package_tree_sha256 is not None
    assert len(provenance.package_tree_sha256) == 64

    assert provenance.repository_available is True
    assert provenance.commit == commit
    assert provenance.branch is not None
    assert provenance.dirty is False
    assert provenance.remote == "https://github.com/example/abmforge.git"


def test_framework_provenance_detects_dirty_runtime_tree(
    tmp_path: Path,
) -> None:
    package_root, _ = _init_framework_repository(tmp_path / "framework-repo")

    clean = FrameworkProvenanceV1.from_package_root(
        package_root,
        version="9.9.9",
    )

    core_path = package_root / "core.py"
    core_path.write_text(
        "VALUE = 2\n",
        encoding="utf-8",
    )

    dirty = FrameworkProvenanceV1.from_package_root(
        package_root,
        version="9.9.9",
    )

    assert clean.dirty is False
    assert dirty.dirty is True
    assert clean.package_tree_sha256 != dirty.package_tree_sha256


def test_framework_provenance_records_installed_distribution(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "site-packages" / "abmforge"
    package_root.mkdir(parents=True)

    (package_root / "__init__.py").write_text(
        '__version__ = "9.9.9"\n',
        encoding="utf-8",
    )
    (package_root / "core.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )

    provenance = FrameworkProvenanceV1.from_package_root(
        package_root,
        version="9.9.9",
    )

    assert provenance.install_mode == "installed-distribution"
    assert provenance.package_tree_sha256 is not None
    assert provenance.repository_available is False
    assert provenance.commit is None
    assert provenance.branch is None
    assert provenance.dirty is None
    assert provenance.remote is None


def test_framework_tree_hash_ignores_python_cache_files(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "site-packages" / "abmforge"
    package_root.mkdir(parents=True)

    (package_root / "__init__.py").write_text(
        '__version__ = "9.9.9"\n',
        encoding="utf-8",
    )
    (package_root / "core.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )

    before = FrameworkProvenanceV1.from_package_root(
        package_root,
        version="9.9.9",
    )

    cache = package_root / "__pycache__"
    cache.mkdir()
    (cache / "core.cpython-311.pyc").write_bytes(b"cache-data")

    after = FrameworkProvenanceV1.from_package_root(
        package_root,
        version="9.9.9",
    )

    assert before.package_tree_sha256 == after.package_tree_sha256


def test_framework_provenance_payload_has_explicit_scope(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "site-packages" / "abmforge"
    package_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text(
        '__version__ = "9.9.9"\n',
        encoding="utf-8",
    )

    payload = FrameworkProvenanceV1.from_package_root(
        package_root,
        version="9.9.9",
    ).to_dict()

    assert payload["schema_version"] == "framework-provenance-v1"
    assert payload["scope"] == "abmforge-framework"
    assert payload["name"] == "abmforge"
    assert payload["version"] == "9.9.9"
    assert payload["install_mode"] == "installed-distribution"
    assert payload["package_tree_sha256"]
