from __future__ import annotations

from pathlib import Path

import pytest

from abmforge.core.model import Model
from abmforge.experiment.scenario import Scenario
from abmforge.repro.manifest import ReproducibilityManifest


class ManifestInputConvergenceModel(Model):
    pass


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def _manifest_from_result(
    result,
    *,
    input_artifacts=None,
    input_root=None,
):
    return ReproducibilityManifest.from_run_result(
        result,
        include_git=False,
        include_packages=False,
        include_command=False,
        input_artifacts=input_artifacts,
        input_root=input_root,
    )


def test_manifest_accepts_inputs_matching_v3_fingerprint(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    scenario = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
        input_artifacts=[input_path],
        input_root=root,
    )

    result = scenario.run()

    manifest = _manifest_from_result(
        result,
        input_artifacts=[input_path],
        input_root=root,
    )

    fingerprint = result.dataset.runs[-1]["execution_fingerprint"]

    assert len(manifest.input_artifacts) == 1
    assert fingerprint["input_artifact_count"] == 1


def test_manifest_rejects_missing_inputs_for_v3_run(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    scenario = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
        input_artifacts=[input_path],
        input_root=root,
    )

    result = scenario.run()

    with pytest.raises(
        ValueError,
        match="declared input identity",
    ):
        _manifest_from_result(result)


def test_manifest_rejects_different_input_set_for_v3_run(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"

    executed_input = _write(
        root / "data" / "executed.csv",
        "value\n1\n",
    )
    different_input = _write(
        root / "data" / "different.csv",
        "value\n1\n",
    )

    scenario = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
        input_artifacts=[executed_input],
        input_root=root,
    )

    result = scenario.run()

    with pytest.raises(
        ValueError,
        match="declared input identity",
    ):
        _manifest_from_result(
            result,
            input_artifacts=[different_input],
            input_root=root,
        )


def test_manifest_rejects_input_changed_after_execution(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    scenario = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
        input_artifacts=[input_path],
        input_root=root,
    )

    result = scenario.run()

    input_path.write_bytes(b"value\n2\n")

    with pytest.raises(
        ValueError,
        match="declared input identity",
    ):
        _manifest_from_result(
            result,
            input_artifacts=[input_path],
            input_root=root,
        )


def test_manifest_accepts_empty_inputs_for_v3_run_without_inputs() -> None:
    scenario = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
    )

    result = scenario.run()

    manifest = _manifest_from_result(result)

    assert manifest.input_artifacts == []


def test_manifest_cannot_retroactively_declare_input_for_v3_run(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    scenario = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
    )

    result = scenario.run()

    with pytest.raises(
        ValueError,
        match="declared input identity",
    ):
        _manifest_from_result(
            result,
            input_artifacts=[input_path],
            input_root=root,
        )


def test_manifest_rejects_mixed_v3_input_identities_across_runs(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"

    first_input = _write(
        root / "data" / "first.csv",
        "value\n1\n",
    )
    second_input = _write(
        root / "data" / "second.csv",
        "value\n2\n",
    )

    first_result = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
        input_artifacts=[first_input],
        input_root=root,
    ).run()

    second_result = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
        input_artifacts=[second_input],
        input_root=root,
    ).run()

    dataset = second_result.dataset
    dataset.runs.insert(
        0,
        dict(first_result.dataset.runs[-1]),
    )

    with pytest.raises(
        ValueError,
        match="declared input identity",
    ):
        ReproducibilityManifest.from_dataset(
            dataset,
            include_git=False,
            include_packages=False,
            include_command=False,
            input_artifacts=[second_input],
            input_root=root,
        )


def test_manifest_rejects_framework_identity_mismatch_for_v3_run() -> None:
    result = Scenario(
        model=ManifestInputConvergenceModel,
        steps=0,
    ).run()

    manifest = _manifest_from_result(result)

    fingerprint = result.dataset.runs[-1]["execution_fingerprint"]
    original_hash = fingerprint["framework_package_tree_sha256"]

    different_hash = "f" * 64 if original_hash != "f" * 64 else "e" * 64

    manifest.framework["package_tree_sha256"] = different_hash

    with pytest.raises(
        ValueError,
        match="framework identity",
    ):
        manifest.validate()
