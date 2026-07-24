from __future__ import annotations

import os
from pathlib import Path

import pytest

from abmforge._internal.filesystem import (
    UnsafePathError,
    ensure_safe_destination,
)


def test_safe_destination_accepts_child_of_root(
    tmp_path: Path,
) -> None:
    root = tmp_path / "archive"
    root.mkdir()

    destination = root / "configs" / "scenario.yaml"

    actual = ensure_safe_destination(
        destination,
        allowed_root=root,
    )

    assert actual == destination.resolve(strict=False)


@pytest.mark.parametrize(
    "relative_path",
    [
        "../outside.txt",
        "../../outside.txt",
        "configs/../../outside.txt",
    ],
)
def test_safe_destination_rejects_parent_traversal(
    tmp_path: Path,
    relative_path: str,
) -> None:
    root = tmp_path / "archive"
    root.mkdir()

    with pytest.raises(UnsafePathError, match="outside"):
        ensure_safe_destination(
            root / relative_path,
            allowed_root=root,
        )


def test_safe_destination_rejects_absolute_path_outside_root(
    tmp_path: Path,
) -> None:
    root = tmp_path / "archive"
    outside = tmp_path / "outside.txt"
    root.mkdir()

    with pytest.raises(UnsafePathError, match="outside"):
        ensure_safe_destination(
            outside,
            allowed_root=root,
        )


def test_safe_destination_rejects_root_itself(
    tmp_path: Path,
) -> None:
    root = tmp_path / "archive"
    root.mkdir()

    with pytest.raises(
        UnsafePathError,
        match="must not be the allowed root",
    ):
        ensure_safe_destination(
            root,
            allowed_root=root,
        )


@pytest.mark.skipif(
    os.name == "nt",
    reason="Windows symlink creation may require Developer Mode.",
)
def test_safe_destination_rejects_symlink_parent(
    tmp_path: Path,
) -> None:
    root = tmp_path / "archive"
    outside = tmp_path / "outside"
    link = root / "configs"

    root.mkdir()
    outside.mkdir()
    link.symlink_to(outside, target_is_directory=True)

    with pytest.raises(UnsafePathError, match="symbolic link"):
        ensure_safe_destination(
            link / "scenario.yaml",
            allowed_root=root,
            reject_symlink_parents=True,
        )


def test_symlink_parent_is_checked_before_resolved_containment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "archive"
    configs = root / "configs"
    destination = configs / "scenario.yaml"

    root.mkdir()
    configs.mkdir()

    original_is_symlink = Path.is_symlink

    def fake_is_symlink(path: Path) -> bool:
        if path == configs:
            return True
        return original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", fake_is_symlink)

    with pytest.raises(UnsafePathError, match="symbolic link"):
        ensure_safe_destination(
            destination,
            allowed_root=root,
        )
