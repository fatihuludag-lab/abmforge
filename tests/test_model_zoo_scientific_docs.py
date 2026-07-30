from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ZOO_DOC = ROOT / "docs" / "model-zoo.md"
SIR_README = ROOT / "model_zoo" / "sir" / "README.md"
SCHELLING_README = ROOT / "model_zoo" / "schelling" / "README.md"
SCIENTIFIC_TESTS = ROOT / "tests" / "test_model_zoo_scientific_validation.py"


def _normalized(path: Path) -> str:
    return " ".join(
        path.read_text(
            encoding="utf-8",
        ).split()
    )


def test_model_zoo_docs_define_scientific_verification_contract() -> None:
    text = _normalized(MODEL_ZOO_DOC)

    expected = [
        "## Scientific verification contract",
        "`tests/test_model_zoo_scientific_validation.py`",
        "### SIR verified properties",
        "### Schelling verified properties",
        "asynchronous random activation",
        "same-seed trajectory reproducibility",
        "metamorphic relations",
        "does not constitute empirical validation or calibration",
        (
            "does not claim that higher homophily produces greater "
            "segregation in every stochastic run"
        ),
    ]

    for statement in expected:
        assert statement in text


def test_sir_readme_matches_runtime_parameters_and_semantics() -> None:
    text = _normalized(SIR_README)

    expected = [
        "| `n_agents` |",
        "| `initial_infected` |",
        "| `infection_prob` |",
        "| `recovery_prob` |",
        "| `steps` |",
        "asynchronous random activation",
        "`S + I + R = N`",
        "Susceptible counts do not increase",
        "Recovered counts do not decrease",
        "No initial infection is an absorbing state",
        "same-seed trajectory reproducibility",
        "does not guarantee a single epidemic peak",
    ]

    for statement in expected:
        assert statement in text

    obsolete = [
        "| population_size |",
        "| infection_probability |",
        "| recovery_probability |",
        "| max_steps |",
    ]

    for statement in obsolete:
        assert statement not in text


def test_schelling_readme_documents_verified_properties_and_limits() -> None:
    text = _normalized(SCHELLING_README)

    expected = [
        "## Scientific Verification",
        "population and vacancy counts are conserved",
        "group-label swap symmetry",
        ("unhappy-household count is non-decreasing as homophily increases"),
        "same-seed trajectory reproducibility",
        ("`happy` is synchronized with the final post-step spatial state"),
        (
            "does not claim that higher homophily produces greater "
            "segregation in every stochastic run"
        ),
    ]

    for statement in expected:
        assert statement in text


def test_model_zoo_docs_reference_executable_scientific_tests() -> None:
    assert SCIENTIFIC_TESTS.exists()

    text = MODEL_ZOO_DOC.read_text(
        encoding="utf-8",
    )

    assert "tests/test_model_zoo_scientific_validation.py" in text

    test_source = SCIENTIFIC_TESTS.read_text(
        encoding="utf-8",
    )

    assert test_source.count("\ndef test_") >= 18
