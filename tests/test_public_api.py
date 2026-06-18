import abmforge


def test_public_api_exports_are_unique() -> None:
    assert len(abmforge.__all__) == len(set(abmforge.__all__))


def test_public_api_exports_exist() -> None:
    for name in abmforge.__all__:
        assert hasattr(abmforge, name), name


def test_core_public_imports() -> None:
    from abmforge import Agent, Experiment, Model, ParameterGrid, Scenario

    assert Agent is not None
    assert Model is not None
    assert Scenario is not None
    assert Experiment is not None
    assert ParameterGrid is not None
