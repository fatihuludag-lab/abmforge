from __future__ import annotations

from abmforge import Model
from abmforge.scheduling import (
    RandomActivation,
    SequentialActivation,
    SimultaneousActivation,
    StagedActivation,
)


def test_base_scheduler_metadata_contract_for_standard_schedulers() -> None:
    model = Model(seed=123)

    for scheduler_cls in (
        SequentialActivation,
        RandomActivation,
        SimultaneousActivation,
    ):
        scheduler = scheduler_cls(model)
        metadata = scheduler.to_metadata()

        assert metadata["schema_version"] == "scheduler-metadata-v1"
        assert metadata["scheduler_type"] == scheduler_cls.__name__
        assert metadata["module"].startswith("abmforge.scheduling")
        assert metadata["attached"] is True


def test_staged_scheduler_metadata_records_stages_and_shuffle() -> None:
    model = Model(seed=123)
    scheduler = StagedActivation(
        model,
        stages=["sense", "decide", "act"],
        shuffle=True,
    )

    metadata = scheduler.to_metadata()

    assert metadata["schema_version"] == "scheduler-metadata-v1"
    assert metadata["scheduler_type"] == "StagedActivation"
    assert metadata["stages"] == ["sense", "decide", "act"]
    assert metadata["shuffle"] is True
    assert metadata["attached"] is True


def test_model_snapshot_records_unattached_scheduler_metadata_by_default() -> None:
    model = Model(seed=123)

    snapshot = model.snapshot()

    assert snapshot["scheduler"] == {
        "schema_version": "scheduler-metadata-v1",
        "attached": False,
    }


def test_model_snapshot_records_attached_scheduler_metadata() -> None:
    model = Model(seed=123)
    model._scheduler = StagedActivation(model, stages=["sense", "act"], shuffle=False)

    snapshot = model.snapshot()

    assert snapshot["scheduler"]["schema_version"] == "scheduler-metadata-v1"
    assert snapshot["scheduler"]["scheduler_type"] == "StagedActivation"
    assert snapshot["scheduler"]["stages"] == ["sense", "act"]
    assert snapshot["scheduler"]["shuffle"] is False
    assert snapshot["scheduler"]["attached"] is True


def test_model_from_snapshot_does_not_restore_scheduler_instance() -> None:
    model = Model(seed=123)
    model._scheduler = StagedActivation(model, stages=["sense", "act"])
    snapshot = model.snapshot()

    restored = Model.from_snapshot(snapshot)

    assert not hasattr(restored, "_scheduler")
    assert restored.snapshot()["scheduler"]["attached"] is False
