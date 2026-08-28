from __future__ import annotations

import json
from pathlib import Path

import pytest

import abmforge
from abmforge import Model, ReproducibilityManifest, Scenario
from abmforge.data.dataset import Dataset
from abmforge.repro import describe_file_artifact, sha256_file


class EmptyModel(Model):
    """Minimal model used for manifest tests."""


def _sample_dataset() -> Dataset:
    dataset = Dataset(run_id="run-test")
    dataset.add_run(
        run_id="run-test",
        scenario="demo",
        model_name="DemoModel",
        parameters={"alpha": 0.1, "beta": 2},
        seed=42,
        status="completed",
    )
    dataset.record_model(step=0, time=0.0, metric="population", value=10)
    dataset.record_agent(
        step=0,
        time=0.0,
        agent_id=1,
        agent_type="Person",
        variable="wealth",
        value=5,
    )
    dataset.record_event(
        step=0,
        time=0.0,
        event_id="event-1",
        owner=1,
        tags=["test"],
        status="executed",
    )
    dataset.record_lifecycle(
        step=0,
        time=0.0,
        event="created",
        agent_id=1,
        details={"agent_type": "Person"},
    )
    return dataset


def test_manifest_from_dataset_contains_required_metadata() -> None:
    dataset = _sample_dataset()

    manifest = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
        metadata={"purpose": "unit-test"},
    )
    data = manifest.to_dict()

    assert data["schema_version"] == "abmforge.manifest.v1"
    assert data["abmforge_version"] == abmforge.__version__
    assert data["dataset_schema_version"] == "abmforge.dataset.v1"
    assert data["dataset_schema_hash"]
    assert data["run_id"] == "run-test"
    assert data["scenario"] == "demo"
    assert data["model_name"] == "DemoModel"
    assert data["seed"] == 42
    assert data["status"] == "completed"
    assert data["parameters_hash"] is not None
    assert data["record_counts"]["runs"] == 1
    assert data["record_counts"]["model_records"] == 1
    assert data["record_counts"]["agent_records"] == 1
    assert data["record_counts"]["event_records"] == 1
    assert data["record_counts"]["lifecycle_records"] == 1
    assert data["record_counts"]["errors"] == 0
    assert data["n_model_records"] == 1
    assert data["n_agent_records"] == 1
    assert data["n_event_records"] == 1
    assert data["n_lifecycle_records"] == 1
    assert data["n_errors"] == 0
    assert data["git"] is None
    assert data["packages"] is None
    assert data["metadata"]["purpose"] == "unit-test"
    assert data["metadata"]["rng_stream_policy"] == "named-rng-streams-v1"


def test_manifest_write_to_directory(tmp_path) -> None:  # type: ignore[no-untyped-def]
    dataset = _sample_dataset()
    manifest = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )

    output_path = manifest.write(tmp_path)

    assert output_path.name == "manifest.json"
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["schema_version"] == "abmforge.manifest.v1"
    assert data["run_id"] == "run-test"
    assert data["n_model_records"] == 1


def test_dataset_write_manifest_uses_manifest_v1(tmp_path) -> None:  # type: ignore[no-untyped-def]
    dataset = _sample_dataset()

    output_path = dataset.write_manifest(tmp_path)
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["schema_version"] == "abmforge.manifest.v1"
    assert data["abmforge_version"] == abmforge.__version__
    assert data["run_id"] == "run-test"
    assert data["record_counts"]["model_records"] == 1
    assert data["record_counts"]["errors"] == 0
    assert data["n_errors"] == 0


def test_manifest_from_run_result() -> None:
    result = Scenario(model=EmptyModel, seed=123, steps=0, name="manifest-test").run()

    manifest = ReproducibilityManifest.from_run_result(
        result,
        include_git=False,
        include_packages=False,
        include_command=False,
    )
    data = manifest.to_dict()

    assert data["schema_version"] == "abmforge.manifest.v1"
    assert data["run_id"] == result.run_id
    assert data["abmforge_version"] == abmforge.__version__
    assert data["metadata"]["run_result_status"] == result.status
    assert data["metadata"]["run_result_steps"] == result.steps
    assert data["metadata"]["rng_stream_policy"] == "named-rng-streams-v1"
    assert data["git"] is None


def test_manifest_content_hash_is_stable_for_same_content() -> None:
    dataset = _sample_dataset()

    manifest_a = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )
    manifest_b = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )

    assert manifest_a.record_hashes == manifest_b.record_hashes


def test_file_artifact_description_uses_relative_paths_and_hashes(tmp_path) -> None:
    artifact_path = tmp_path / "configs" / "scenario.yaml"
    artifact_path.parent.mkdir()
    artifact_path.write_text("model: demo.Model\nrun:\n  steps: 1\n", encoding="utf-8")

    artifact = describe_file_artifact(
        artifact_path,
        root=tmp_path,
        role="input_config",
    )

    assert artifact["path"] == "configs/scenario.yaml"
    assert artifact["role"] == "input_config"
    assert artifact["size_bytes"] == artifact_path.stat().st_size
    assert artifact["sha256"] == sha256_file(artifact_path)


def test_manifest_validates_artifact_records() -> None:
    dataset = _sample_dataset()
    manifest = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )
    manifest.artifacts = [
        {
            "path": "configs/scenario.yaml",
            "sha256": "0" * 64,
            "size_bytes": 10,
            "role": "input_config",
        }
    ]

    manifest.validate()


def test_manifest_rejects_invalid_artifact_records() -> None:
    dataset = _sample_dataset()
    manifest = ReproducibilityManifest.from_dataset(
        dataset,
        include_git=False,
        include_packages=False,
        include_command=False,
    )
    manifest.artifacts = [{"path": "configs/scenario.yaml"}]

    with pytest.raises(ValueError, match="sha256"):
        manifest.validate()


def test_manifest_rng_stream_policy_cannot_be_overridden() -> None:
    manifest = ReproducibilityManifest.from_dataset(
        _sample_dataset(),
        include_git=False,
        include_packages=False,
        include_command=False,
        metadata={
            "rng_stream_policy": "user-supplied-invalid-policy",
        },
    )

    assert manifest.metadata["rng_stream_policy"] == "named-rng-streams-v1"


def test_manifest_docs_describe_named_rng_policy() -> None:
    text = Path("docs/reproducibility-manifest-v1.md").read_text(
        encoding="utf-8",
    )
    normalized = " ".join(text.split())

    expected = [
        "`metadata.rng_stream_policy`",
        "`named-rng-streams-v1`",
        "does not store generator continuation state",
        "Snapshots store RNG continuation state",
    ]

    for statement in expected:
        assert statement in normalized


def test_manifest_from_run_result_uses_model_source_repository_not_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import importlib
    import subprocess
    import sys

    def init_repository(
        path: Path,
        *,
        filename: str,
        content: str,
    ) -> str:
        path.mkdir()
        (path / filename).write_text(content, encoding="utf-8")

        subprocess.run(
            ["git", "init", "-q"],
            cwd=path,
            check=True,
        )
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
        subprocess.run(
            ["git", "add", filename],
            cwd=path,
            check=True,
        )
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

    source_repo = tmp_path / "source-repo"
    source_commit = init_repository(
        source_repo,
        filename="source_model.py",
        content=("from abmforge import Model\n\nclass SourceRepositoryModel(Model):\n    pass\n"),
    )

    working_repo = tmp_path / "working-repo"
    working_commit = init_repository(
        working_repo,
        filename="README.md",
        content="unrelated working repository\n",
    )

    assert source_commit != working_commit

    sys.path.insert(0, str(source_repo))
    try:
        source_module = importlib.import_module("source_model")

        result = Scenario(
            model=source_module.SourceRepositoryModel,
            seed=123,
            steps=0,
            name="source-provenance",
        ).run()

        monkeypatch.chdir(working_repo)

        manifest = ReproducibilityManifest.from_run_result(
            result,
            include_git=True,
            include_packages=False,
            include_command=False,
        )
    finally:
        sys.path.remove(str(source_repo))
        sys.modules.pop("source_model", None)

    assert manifest.git is not None
    assert manifest.git["schema_version"] == ("source-repository-provenance-v1")
    assert manifest.git["scope"] == "model-source"
    assert manifest.git["source_available"] is True
    assert manifest.git["source_path"] == "source_model.py"
    assert manifest.git["source_sha256"]
    assert manifest.git["available"] is True
    assert manifest.git["commit"] == source_commit


def test_manifest_from_run_result_records_input_artifact_checksums(
    tmp_path: Path,
) -> None:
    input_root = tmp_path / "study-inputs"
    input_path = input_root / "data" / "observations.csv"
    input_path.parent.mkdir(parents=True)
    input_path.write_text(
        "agent_id,value\n1,10\n2,20\n",
        encoding="utf-8",
    )

    result = Scenario(
        model=EmptyModel,
        seed=123,
        steps=0,
        name="input-provenance",
    ).run()

    manifest = ReproducibilityManifest.from_run_result(
        result,
        include_git=False,
        include_packages=False,
        include_command=False,
        input_artifacts=[input_path],
        input_root=input_root,
    )
    data = manifest.to_dict()

    assert data["input_artifact_count"] == 1
    assert data["input_artifacts"] == [
        {
            "schema_version": "input-artifact-v1",
            "path": "data/observations.csv",
            "role": "input",
            "size_bytes": input_path.stat().st_size,
            "sha256": sha256_file(input_path),
        }
    ]


def test_manifest_contains_framework_provenance() -> None:
    manifest = ReproducibilityManifest.from_dataset(
        _sample_dataset(),
        include_git=False,
        include_packages=False,
        include_command=False,
    )

    data = manifest.to_dict()
    framework = data["framework"]

    assert data["git"] is None
    assert framework["schema_version"] == "framework-provenance-v1"
    assert framework["scope"] == "abmforge-framework"
    assert framework["name"] == "abmforge"
    assert framework["version"] == abmforge.__version__
    assert framework["install_mode"] in {
        "source-checkout",
        "installed-distribution",
        "unavailable",
    }

    if framework["package_tree_sha256"] is not None:
        assert len(framework["package_tree_sha256"]) == 64


def test_run_result_manifest_framework_is_independent_of_git_option() -> None:
    result = Scenario(
        model=EmptyModel,
        seed=123,
        steps=0,
        name="framework-manifest-test",
    ).run()

    manifest = ReproducibilityManifest.from_run_result(
        result,
        include_git=False,
        include_packages=False,
        include_command=False,
    )

    data = manifest.to_dict()

    assert data["git"] is None
    assert data["framework"]["scope"] == "abmforge-framework"
    assert data["framework"]["version"] == abmforge.__version__


def test_manifest_rejects_framework_version_mismatch() -> None:
    manifest = ReproducibilityManifest.from_dataset(
        _sample_dataset(),
        include_git=False,
        include_packages=False,
        include_command=False,
    )

    manifest.framework["version"] = "0.0.0-invalid"

    with pytest.raises(
        ValueError,
        match="framework.version must equal abmforge_version",
    ):
        manifest.validate()


def test_manifest_rejects_invalid_framework_tree_hash() -> None:
    manifest = ReproducibilityManifest.from_dataset(
        _sample_dataset(),
        include_git=False,
        include_packages=False,
        include_command=False,
    )

    manifest.framework["package_tree_sha256"] = "not-a-sha256"

    with pytest.raises(
        ValueError,
        match="framework.package_tree_sha256",
    ):
        manifest.validate()


def test_manifest_docs_describe_framework_provenance() -> None:
    text = Path("docs/reproducibility-manifest-v1.md").read_text(
        encoding="utf-8",
    )
    normalized = " ".join(text.split())

    expected = [
        "`framework`",
        "`framework-provenance-v1`",
        "`package_tree_sha256`",
        "independent of the legacy `git` field",
        "`framework.version`",
        "Legacy Manifest V1",
        "must not be fabricated",
    ]

    for statement in expected:
        assert statement in normalized
