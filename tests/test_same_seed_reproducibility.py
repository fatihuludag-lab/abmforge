import hashlib
import json
from typing import Any

from abmforge import Model, Scenario

_UNSTABLE_FIELDS = {
    "run_id",
    "started_at",
    "ended_at",
    "created_at",
    "finished_at",
}


class RandomMetricModel(Model):
    """Small stochastic model used to test seed reproducibility."""

    def setup(self) -> None:
        self.current_draw = 0.0
        self.record.metric("draw", lambda model: model.current_draw)

    def step(self) -> None:
        self.current_draw = float(self.rng.random())


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key not in _UNSTABLE_FIELDS}


def _canonical_hash(data: Any) -> str:
    payload = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def _dataset_hash(result: Any) -> str:
    dataset = result.dataset

    payload = {
        "runs": [_normalize_record(record) for record in dataset.runs],
        "model_records": [_normalize_record(record) for record in dataset.model_records],
        "agent_records": [_normalize_record(record) for record in dataset.agent_records],
        "event_records": [_normalize_record(record) for record in dataset.event_records],
        "lifecycle_records": [_normalize_record(record) for record in dataset.lifecycle_records],
        "errors": [_normalize_record(record) for record in dataset.errors],
    }

    return _canonical_hash(payload)


def _run_random_metric_model(seed: int) -> Any:
    scenario = Scenario(
        model=RandomMetricModel,
        parameters={},
        seed=seed,
        steps=10,
        name="random_metric_reproducibility",
    )

    return scenario.run()


def test_same_seed_produces_same_dataset_hash() -> None:
    result_1 = _run_random_metric_model(seed=42)
    result_2 = _run_random_metric_model(seed=42)

    assert result_1.status == "completed"
    assert result_2.status == "completed"
    assert _dataset_hash(result_1) == _dataset_hash(result_2)


def test_different_seed_produces_different_dataset_hash() -> None:
    result_1 = _run_random_metric_model(seed=42)
    result_2 = _run_random_metric_model(seed=43)

    assert result_1.status == "completed"
    assert result_2.status == "completed"
    assert _dataset_hash(result_1) != _dataset_hash(result_2)
