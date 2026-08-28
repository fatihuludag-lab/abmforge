from __future__ import annotations

from abmforge.core.model import Model
from abmforge.repro.execution_fingerprint import (
    ExecutionFingerprintV1,
    ExecutionFingerprintV2,
)


class FingerprintV2TestModel(Model):
    pass


FRAMEWORK_HASH_A = "a" * 64
FRAMEWORK_HASH_B = "b" * 64


def _create_v2(
    *,
    framework_hash: str | None = FRAMEWORK_HASH_A,
) -> ExecutionFingerprintV2:
    return ExecutionFingerprintV2.create(
        model=FingerprintV2TestModel,
        scenario="framework-aware",
        seed=101,
        steps=10,
        parameters={"alpha": 1, "beta": 2},
        framework_version="0.3.0a2.dev0",
        framework_package_tree_sha256=framework_hash,
    )


def test_v2_uses_new_schema() -> None:
    fingerprint = _create_v2()

    assert fingerprint.schema_version == "execution-fingerprint-v2"
    assert fingerprint.trusted is True


def test_v2_digest_changes_when_framework_tree_changes() -> None:
    first = _create_v2(framework_hash=FRAMEWORK_HASH_A)
    second = _create_v2(framework_hash=FRAMEWORK_HASH_B)

    assert first.framework_version == second.framework_version
    assert first.framework_package_tree_sha256 != (second.framework_package_tree_sha256)
    assert first.digest != second.digest


def test_v2_round_trip_checks_integrity() -> None:
    fingerprint = _create_v2()
    payload = fingerprint.to_dict()

    assert ExecutionFingerprintV2.from_dict(payload) == fingerprint

    payload["framework_package_tree_sha256"] = FRAMEWORK_HASH_B

    assert ExecutionFingerprintV2.from_dict(payload) is None


def test_v2_is_untrusted_without_framework_tree_identity() -> None:
    fingerprint = _create_v2(framework_hash=None)

    assert fingerprint.trusted is False
    assert fingerprint.framework_package_tree_sha256 is None


def test_v1_does_not_accept_v2_payload() -> None:
    payload = _create_v2().to_dict()

    assert ExecutionFingerprintV1.from_dict(payload) is None


def test_scenario_execution_fingerprint_uses_v2() -> None:
    from abmforge.experiment.scenario import Scenario

    scenario = Scenario(
        model=FingerprintV2TestModel,
        parameters={"alpha": 1},
        seed=501,
        steps=4,
        name="scenario-v2",
    )

    fingerprint = scenario.execution_fingerprint()

    assert isinstance(fingerprint, ExecutionFingerprintV2)
    assert fingerprint.schema_version == "execution-fingerprint-v2"
    assert fingerprint.framework_version
    assert fingerprint.framework_package_tree_sha256 is not None
    assert fingerprint.trusted is True


def test_scenario_run_persists_v2_fingerprint() -> None:
    from abmforge.experiment.scenario import Scenario

    scenario = Scenario(
        model=FingerprintV2TestModel,
        parameters={"alpha": 1},
        seed=502,
        steps=0,
        name="scenario-run-v2",
    )

    result = scenario.run()
    payload = result.dataset.runs[-1]["execution_fingerprint"]

    assert payload["schema_version"] == "execution-fingerprint-v2"
    assert payload["framework_version"]
    assert payload["framework_package_tree_sha256"]
    assert ExecutionFingerprintV2.from_dict(payload) is not None


def test_runtime_framework_execution_identity_is_cached(
    monkeypatch,
) -> None:
    from types import SimpleNamespace

    import abmforge.repro.execution_fingerprint as fingerprint_module

    calls = 0

    def fake_from_runtime():
        nonlocal calls
        calls += 1
        return SimpleNamespace(
            version="0.3.0a2.dev0",
            package_tree_sha256="c" * 64,
        )

    fingerprint_module.runtime_framework_execution_identity.cache_clear()

    monkeypatch.setattr(
        fingerprint_module.FrameworkProvenanceV1,
        "from_runtime",
        staticmethod(fake_from_runtime),
    )

    try:
        first = fingerprint_module.runtime_framework_execution_identity()
        second = fingerprint_module.runtime_framework_execution_identity()
    finally:
        fingerprint_module.runtime_framework_execution_identity.cache_clear()

    assert calls == 1
    assert first is second
    assert first.version == "0.3.0a2.dev0"
    assert first.package_tree_sha256 == "c" * 64
    assert first.trusted is True


def test_current_execution_fingerprint_schema_constant_is_v2() -> None:
    from abmforge.repro.execution_fingerprint import (
        EXECUTION_FINGERPRINT_SCHEMA_VERSION,
        EXECUTION_FINGERPRINT_V1_SCHEMA_VERSION,
        EXECUTION_FINGERPRINT_V2_SCHEMA_VERSION,
    )

    assert EXECUTION_FINGERPRINT_V1_SCHEMA_VERSION == "execution-fingerprint-v1"
    assert (
        EXECUTION_FINGERPRINT_SCHEMA_VERSION
        == EXECUTION_FINGERPRINT_V2_SCHEMA_VERSION
        == "execution-fingerprint-v2"
    )


def test_v2_rejects_invalid_model_source_identity() -> None:
    fingerprint = ExecutionFingerprintV2(
        model_name="InvalidModel",
        model_module="invalid.module",
        model_qualname="InvalidModel",
        model_source_kind="invalid-source-kind",
        model_source_sha256="not-a-sha256",
        scenario="invalid-source",
        seed=1,
        steps=1,
        parameters_sha256="a" * 64,
        framework_version="0.3.0a2.dev0",
        framework_package_tree_sha256="b" * 64,
    )

    assert fingerprint.trusted is False
    assert ExecutionFingerprintV2.from_dict(fingerprint.to_dict()) is None


def test_v2_rejects_invalid_parameter_digest() -> None:
    fingerprint = ExecutionFingerprintV2(
        model_name="InvalidParameters",
        model_module="invalid.parameters",
        model_qualname="InvalidParameters",
        model_source_kind="module-file-sha256",
        model_source_sha256="a" * 64,
        scenario="invalid-parameters",
        seed=1,
        steps=1,
        parameters_sha256="not-a-sha256",
        framework_version="0.3.0a2.dev0",
        framework_package_tree_sha256="b" * 64,
    )

    assert fingerprint.trusted is False
    assert ExecutionFingerprintV2.from_dict(fingerprint.to_dict()) is None
