import pytest

from abmforge import SALibProblem, sample_sobol


def test_salib_problem_to_dict():
    problem = SALibProblem(
        bounds={
            "density": (0.4, 0.9),
            "homophily": (0.1, 0.8),
        }
    )

    assert problem.names == ["density", "homophily"]
    assert problem.to_dict() == {
        "num_vars": 2,
        "names": ["density", "homophily"],
        "bounds": [[0.4, 0.9], [0.1, 0.8]],
    }


def test_salib_missing_dependency_message():
    pytest.importorskip("SALib")

    problem = SALibProblem(bounds={"x": (0.0, 1.0)})
    samples = sample_sobol(problem, n=4, seed=1)

    assert samples
    assert "x" in samples[0]
