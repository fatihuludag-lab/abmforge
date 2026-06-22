from __future__ import annotations

from importlib.metadata import version


def test_public_imports() -> None:
    import abmforge
    from abmforge import (
        DATASET_SCHEMA_VERSION,
        Agent,
        AgentCollection,
        Dataset,
        DatasetSchemaV1,
        Experiment,
        ExperimentArchive,
        ExperimentResult,
        GridWorld,
        Model,
        NetworkSpace,
        ParameterGrid,
        Recorder,
        RunResult,
        Scenario,
        SchemaValidationError,
    )

    assert abmforge.__version__ == version("abmforge")
    assert DATASET_SCHEMA_VERSION == "abmforge.dataset.v1"
    assert Agent is not None
    assert AgentCollection is not None
    assert Model is not None
    assert GridWorld is not None
    assert NetworkSpace is not None
    assert Scenario is not None
    assert Experiment is not None
    assert ExperimentArchive is not None
    assert ExperimentResult is not None
    assert ParameterGrid is not None
    assert RunResult is not None
    assert Dataset is not None
    assert Recorder is not None
    assert DatasetSchemaV1 is not None
    assert SchemaValidationError is not None


def test_public_api_all_exports_are_importable() -> None:
    import abmforge

    for name in abmforge.__all__:
        assert hasattr(abmforge, name), name


def test_data_api_is_available_from_root_package() -> None:
    from abmforge import DATASET_SCHEMA_VERSION, Dataset, Recorder
    from abmforge.data import (
        DATASET_SCHEMA_VERSION as DATASET_SCHEMA_VERSION_FROM_DATA,
    )
    from abmforge.data import (
        Dataset as DatasetFromData,
    )
    from abmforge.data import (
        Recorder as RecorderFromData,
    )

    assert Dataset is DatasetFromData
    assert Recorder is RecorderFromData
    assert DATASET_SCHEMA_VERSION == DATASET_SCHEMA_VERSION_FROM_DATA
