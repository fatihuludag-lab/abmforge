from __future__ import annotations

from pathlib import Path

import pytest

from abmforge.repro import InputArtifactProvenanceV1


def test_input_artifact_provenance_uses_root_relative_path(
    tmp_path: Path,
) -> None:
    input_root = tmp_path / "inputs"
    input_path = input_root / "data" / "observations.csv"
    input_path.parent.mkdir(parents=True)
    input_path.write_text("agent_id,value\n1,10\n", encoding="utf-8")

    provenance = InputArtifactProvenanceV1.from_path(
        input_path,
        root=input_root,
    )

    assert provenance.path == "data/observations.csv"
    assert provenance.role == "input"
    assert provenance.size_bytes == input_path.stat().st_size
    assert len(provenance.sha256) == 64


def test_input_artifact_provenance_changes_with_file_content(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "input.csv"
    input_path.write_text("value\n1\n", encoding="utf-8")
    first = InputArtifactProvenanceV1.from_path(input_path)

    input_path.write_text("value\n2\n", encoding="utf-8")
    second = InputArtifactProvenanceV1.from_path(input_path)

    assert first.sha256 != second.sha256


def test_input_artifact_provenance_rejects_path_outside_root(
    tmp_path: Path,
) -> None:
    input_root = tmp_path / "inputs"
    input_root.mkdir()
    outside = tmp_path / "outside.csv"
    outside.write_text("value\n1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside input_root"):
        InputArtifactProvenanceV1.from_path(
            outside,
            root=input_root,
        )


def test_input_artifact_provenance_rejects_missing_file(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.csv"

    with pytest.raises(ValueError, match="does not exist"):
        InputArtifactProvenanceV1.from_path(missing)


def test_input_artifact_provenance_dict_is_versioned(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "input.csv"
    input_path.write_text("value\n1\n", encoding="utf-8")

    payload = InputArtifactProvenanceV1.from_path(input_path).to_dict()

    assert payload["schema_version"] == "input-artifact-v1"
    assert payload["role"] == "input"
    assert payload["path"] == input_path.as_posix()
    assert payload["size_bytes"] == input_path.stat().st_size
    assert len(payload["sha256"]) == 64
