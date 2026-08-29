from __future__ import annotations

from pathlib import Path

from abmforge.core.model import Model
from abmforge.repro.execution_fingerprint import (
    ExecutionFingerprintV2,
    ExecutionFingerprintV3,
)
from abmforge.repro.input_provenance import DeclaredInputIdentityV1


class FingerprintV3TestModel(Model):
    pass


FRAMEWORK_HASH = "a" * 64


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def _create_v3(
    declared_inputs: DeclaredInputIdentityV1,
) -> ExecutionFingerprintV3:
    return ExecutionFingerprintV3.create(
        model=FingerprintV3TestModel,
        scenario="input-aware",
        seed=101,
        steps=10,
        parameters={"alpha": 1},
        framework_version="0.3.0a2.dev0",
        framework_package_tree_sha256=FRAMEWORK_HASH,
        declared_inputs=declared_inputs,
    )


def test_v3_uses_new_schema_and_declared_input_identity() -> None:
    declared = DeclaredInputIdentityV1.from_paths([])

    fingerprint = _create_v3(declared)

    assert fingerprint.schema_version == "execution-fingerprint-v3"
    assert fingerprint.declared_input_schema_version == "declared-input-identity-v1"
    assert fingerprint.input_artifact_count == 0
    assert fingerprint.input_artifacts_sha256 == declared.artifacts_sha256
    assert fingerprint.trusted is True


def test_v3_digest_changes_when_declared_input_content_changes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(
        root / "data" / "observations.csv",
        "value\n1\n",
    )

    first_inputs = DeclaredInputIdentityV1.from_paths(
        [input_path],
        root=root,
    )
    first = _create_v3(first_inputs)

    input_path.write_bytes(b"value\n2\n")

    second_inputs = DeclaredInputIdentityV1.from_paths(
        [input_path],
        root=root,
    )
    second = _create_v3(second_inputs)

    assert first_inputs.artifacts_sha256 != second_inputs.artifacts_sha256
    assert first.digest != second.digest


def test_v3_digest_ignores_declared_input_order(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    first_path = _write(root / "data" / "a.csv", "value\n1\n")
    second_path = _write(root / "data" / "b.csv", "value\n2\n")

    first_inputs = DeclaredInputIdentityV1.from_paths(
        [first_path, second_path],
        root=root,
    )
    second_inputs = DeclaredInputIdentityV1.from_paths(
        [second_path, first_path],
        root=root,
    )

    first = _create_v3(first_inputs)
    second = _create_v3(second_inputs)

    assert first_inputs.artifacts_sha256 == second_inputs.artifacts_sha256
    assert first.digest == second.digest


def test_v3_round_trip_checks_declared_input_integrity(
    tmp_path: Path,
) -> None:
    root = tmp_path / "study"
    input_path = _write(root / "data" / "input.csv", "value\n1\n")

    fingerprint = _create_v3(
        DeclaredInputIdentityV1.from_paths(
            [input_path],
            root=root,
        )
    )
    payload = fingerprint.to_dict()

    assert ExecutionFingerprintV3.from_dict(payload) == fingerprint

    payload["input_artifacts_sha256"] = "b" * 64

    assert ExecutionFingerprintV3.from_dict(payload) is None


def test_v3_rejects_invalid_declared_input_digest() -> None:
    fingerprint = ExecutionFingerprintV3(
        model_name="InvalidInputs",
        model_module="invalid.inputs",
        model_qualname="InvalidInputs",
        model_source_kind="module-file-sha256",
        model_source_sha256="1" * 64,
        scenario="invalid-inputs",
        seed=1,
        steps=1,
        parameters_sha256="2" * 64,
        framework_version="0.3.0a2.dev0",
        framework_package_tree_sha256="3" * 64,
        declared_input_schema_version="declared-input-identity-v1",
        input_artifact_count=1,
        input_artifacts_sha256="not-a-sha256",
    )

    assert fingerprint.trusted is False
    assert ExecutionFingerprintV3.from_dict(fingerprint.to_dict()) is None


def test_v3_rejects_unsupported_declared_input_schema() -> None:
    fingerprint = ExecutionFingerprintV3(
        model_name="InvalidInputs",
        model_module="invalid.inputs",
        model_qualname="InvalidInputs",
        model_source_kind="module-file-sha256",
        model_source_sha256="1" * 64,
        scenario="invalid-inputs",
        seed=1,
        steps=1,
        parameters_sha256="2" * 64,
        framework_version="0.3.0a2.dev0",
        framework_package_tree_sha256="3" * 64,
        declared_input_schema_version="declared-input-identity-v999",
        input_artifact_count=0,
        input_artifacts_sha256="4" * 64,
    )

    assert fingerprint.trusted is False
    assert ExecutionFingerprintV3.from_dict(fingerprint.to_dict()) is None


def test_v2_does_not_accept_v3_payload() -> None:
    fingerprint = _create_v3(DeclaredInputIdentityV1.from_paths([]))

    assert ExecutionFingerprintV2.from_dict(fingerprint.to_dict()) is None


def test_v3_does_not_accept_v2_payload() -> None:
    fingerprint = ExecutionFingerprintV2.create(
        model=FingerprintV3TestModel,
        scenario="input-aware",
        seed=101,
        steps=10,
        parameters={"alpha": 1},
        framework_version="0.3.0a2.dev0",
        framework_package_tree_sha256=FRAMEWORK_HASH,
    )

    assert ExecutionFingerprintV3.from_dict(fingerprint.to_dict()) is None


def test_execution_fingerprint_v3_digest_contract_is_immutable() -> None:
    fingerprint = ExecutionFingerprintV3(
        model_name="ContractModel",
        model_module="example.contract",
        model_qualname="ContractModel",
        model_source_kind="module-file-sha256",
        model_source_sha256="1" * 64,
        scenario="contract",
        seed=17,
        steps=23,
        parameters_sha256="2" * 64,
        framework_version="0.3.0a2.dev0",
        framework_package_tree_sha256="3" * 64,
        declared_input_schema_version="declared-input-identity-v1",
        input_artifact_count=2,
        input_artifacts_sha256="4" * 64,
    )

    assert fingerprint.schema_version == "execution-fingerprint-v3"
    assert fingerprint.digest == "a99c99266c8e5615d20f29e6c04ab4bd94c87f404f11597fa26850a5cd343751"


def test_execution_fingerprint_v3_is_exported_from_repro() -> None:
    from abmforge.repro import (
        EXECUTION_FINGERPRINT_V3_SCHEMA_VERSION,
    )
    from abmforge.repro import (
        ExecutionFingerprintV3 as PublicExecutionFingerprintV3,
    )

    assert EXECUTION_FINGERPRINT_V3_SCHEMA_VERSION == "execution-fingerprint-v3"
    assert PublicExecutionFingerprintV3 is ExecutionFingerprintV3
