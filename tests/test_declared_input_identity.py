from __future__ import annotations

from pathlib import Path

import pytest

from abmforge.repro.input_provenance import DeclaredInputIdentityV1


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def test_declared_input_identity_is_order_independent(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    first_path = _write(root / "data" / "a.csv", "value\n1\n")
    second_path = _write(root / "config" / "b.json", '{"mode":"strict"}\n')

    first = DeclaredInputIdentityV1.from_paths(
        [first_path, second_path],
        root=root,
    )
    second = DeclaredInputIdentityV1.from_paths(
        [second_path, first_path],
        root=root,
    )

    assert first.schema_version == "declared-input-identity-v1"
    assert first.artifact_count == 2
    assert [artifact.path for artifact in first.artifacts] == [
        "config/b.json",
        "data/a.csv",
    ]
    assert first.artifacts_sha256 == second.artifacts_sha256


def test_declared_input_identity_changes_with_file_content(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(root / "data" / "observations.csv", "value\n1\n")

    first = DeclaredInputIdentityV1.from_paths(
        [input_path],
        root=root,
    )

    input_path.write_text("value\n2\n", encoding="utf-8")

    second = DeclaredInputIdentityV1.from_paths(
        [input_path],
        root=root,
    )

    assert first.artifacts_sha256 != second.artifacts_sha256


def test_declared_input_identity_changes_with_portable_path(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    first_path = _write(root / "data" / "first.csv", "value\n1\n")
    second_path = _write(root / "data" / "second.csv", "value\n1\n")

    first = DeclaredInputIdentityV1.from_paths(
        [first_path],
        root=root,
    )
    second = DeclaredInputIdentityV1.from_paths(
        [second_path],
        root=root,
    )

    assert first.artifacts[0].sha256 == second.artifacts[0].sha256
    assert first.artifacts_sha256 != second.artifacts_sha256


def test_declared_input_identity_is_independent_of_absolute_root(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "machine-a" / "study"
    second_root = tmp_path / "machine-b" / "study"

    first_path = _write(
        first_root / "data" / "observations.csv",
        "value\n1\n",
    )
    second_path = _write(
        second_root / "data" / "observations.csv",
        "value\n1\n",
    )

    first = DeclaredInputIdentityV1.from_paths(
        [first_path],
        root=first_root,
    )
    second = DeclaredInputIdentityV1.from_paths(
        [second_path],
        root=second_root,
    )

    assert first.artifacts[0].path == "data/observations.csv"
    assert second.artifacts[0].path == "data/observations.csv"
    assert first.artifacts_sha256 == second.artifacts_sha256


def test_declared_input_identity_requires_root_for_declared_inputs(
    tmp_path: Path,
) -> None:
    input_path = _write(tmp_path / "input.csv", "value\n1\n")

    with pytest.raises(
        ValueError,
        match="input_root is required",
    ):
        DeclaredInputIdentityV1.from_paths([input_path])


def test_declared_input_identity_rejects_duplicate_portable_paths(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(root / "data" / "input.csv", "value\n1\n")

    with pytest.raises(
        ValueError,
        match="Duplicate declared input path",
    ):
        DeclaredInputIdentityV1.from_paths(
            [input_path, input_path],
            root=root,
        )


def test_declared_input_identity_empty_set_is_stable() -> None:
    first = DeclaredInputIdentityV1.from_paths([])
    second = DeclaredInputIdentityV1.from_paths([])

    assert first.artifact_count == 0
    assert first.artifacts == ()
    assert len(first.artifacts_sha256) == 64
    assert first.artifacts_sha256 == second.artifacts_sha256


def test_declared_input_identity_wire_contract_is_stable(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "input.csv",
        "value\n1\n",
    )

    identity = DeclaredInputIdentityV1.from_paths(
        [input_path],
        root=root,
    )

    assert identity.artifacts[0].sha256 == (
        "1a80986111952a11d02e84dbed98ae00f279469aad0615d17fa81911f8a6b428"
    )
    assert identity.artifacts_sha256 == (
        "85db28b1104f507f9ca6ba3ba6cdfcc4f4cf6b2e169b23a14123e5c791e4abc0"
    )


@pytest.mark.parametrize(
    "scalar_path",
    [
        "input.csv",
        Path("input.csv"),
    ],
)
def test_declared_input_identity_rejects_scalar_path_argument(
    scalar_path,
) -> None:
    with pytest.raises(
        TypeError,
        match="sequence of paths",
    ):
        DeclaredInputIdentityV1.from_paths(
            scalar_path,
        )


def test_declared_input_identity_is_exported_from_repro() -> None:
    from abmforge.repro import (
        DeclaredInputIdentityV1 as PublicDeclaredInputIdentityV1,
    )

    assert PublicDeclaredInputIdentityV1 is DeclaredInputIdentityV1
