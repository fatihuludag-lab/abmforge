from __future__ import annotations

import importlib
import shutil
import sys
from textwrap import dedent

from abmforge.core.model import Model
from abmforge.repro.execution_fingerprint import ExecutionFingerprintV1


class FingerprintTestModel(Model):
    def setup(self) -> None:
        self.value = 0

    def step(self) -> None:
        self.value += 1


def test_execution_fingerprint_is_stable_for_parameter_order() -> None:
    first = ExecutionFingerprintV1.create(
        model=FingerprintTestModel,
        scenario="baseline",
        seed=101,
        steps=10,
        parameters={"alpha": 1, "beta": 2},
    )
    second = ExecutionFingerprintV1.create(
        model=FingerprintTestModel,
        scenario="baseline",
        seed=101,
        steps=10,
        parameters={"beta": 2, "alpha": 1},
    )

    assert first.trusted is True
    assert first.digest == second.digest
    assert first.parameters_sha256 == second.parameters_sha256


def test_execution_fingerprint_changes_with_execution_inputs() -> None:
    baseline = ExecutionFingerprintV1.create(
        model=FingerprintTestModel,
        scenario="baseline",
        seed=101,
        steps=10,
        parameters={"alpha": 1},
    )
    changed_seed = ExecutionFingerprintV1.create(
        model=FingerprintTestModel,
        scenario="baseline",
        seed=102,
        steps=10,
        parameters={"alpha": 1},
    )
    changed_steps = ExecutionFingerprintV1.create(
        model=FingerprintTestModel,
        scenario="baseline",
        seed=101,
        steps=11,
        parameters={"alpha": 1},
    )
    changed_parameters = ExecutionFingerprintV1.create(
        model=FingerprintTestModel,
        scenario="baseline",
        seed=101,
        steps=10,
        parameters={"alpha": 2},
    )

    assert baseline.digest != changed_seed.digest
    assert baseline.digest != changed_steps.digest
    assert baseline.digest != changed_parameters.digest


def test_execution_fingerprint_detects_model_source_change(tmp_path) -> None:
    module_name = f"fingerprint_source_{tmp_path.name.replace('-', '_')}"
    module_path = tmp_path / f"{module_name}.py"

    def write_model(*, increment: int) -> None:
        module_path.write_text(
            dedent(
                f"""
                from abmforge.core.model import Model


                class FingerprintedModel(Model):
                    def setup(self) -> None:
                        self.value = 0

                    def step(self) -> None:
                        self.value += {increment}
                """
            ),
            encoding="utf-8",
        )
        importlib.invalidate_caches()

    sys.path.insert(0, str(tmp_path))
    try:
        write_model(increment=1)
        first_module = importlib.import_module(module_name)
        first = ExecutionFingerprintV1.create(
            model=first_module.FingerprintedModel,
            scenario="source-change",
            seed=201,
            steps=2,
            parameters={"alpha": 1},
        )

        sys.modules.pop(module_name, None)
        shutil.rmtree(tmp_path / "__pycache__", ignore_errors=True)

        write_model(increment=2)
        second_module = importlib.import_module(module_name)
        second = ExecutionFingerprintV1.create(
            model=second_module.FingerprintedModel,
            scenario="source-change",
            seed=201,
            steps=2,
            parameters={"alpha": 1},
        )
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop(module_name, None)

    assert first.trusted is True
    assert second.trusted is True
    assert first.model_source_sha256 != second.model_source_sha256
    assert first.digest != second.digest


def test_execution_fingerprint_round_trip_checks_integrity() -> None:
    fingerprint = ExecutionFingerprintV1.create(
        model=FingerprintTestModel,
        scenario="round-trip",
        seed=301,
        steps=5,
        parameters={"alpha": 1},
    )

    payload = fingerprint.to_dict()

    assert ExecutionFingerprintV1.from_dict(payload) == fingerprint

    payload["steps"] = 500

    assert ExecutionFingerprintV1.from_dict(payload) is None


def test_execution_fingerprint_is_untrusted_when_source_is_unavailable() -> None:
    dynamic_model = type(
        "DynamicModel",
        (Model,),
        {"__module__": "module_that_does_not_exist"},
    )

    fingerprint = ExecutionFingerprintV1.create(
        model=dynamic_model,
        scenario="dynamic",
        seed=401,
        steps=1,
        parameters={},
    )

    assert fingerprint.trusted is False
    assert fingerprint.model_source_sha256 is None
