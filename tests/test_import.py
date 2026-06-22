def test_public_imports() -> None:
    import abmforge
    from abmforge import Agent, GridWorld, Model, Scenario

    assert abmforge.__version__ == "0.2.0a4.dev0"
    assert Agent is not None
    assert Model is not None
    assert GridWorld is not None
    assert Scenario is not None
