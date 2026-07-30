from __future__ import annotations

from collections import Counter
from typing import Any, cast

import pytest
from model_zoo.schelling.model import Household, SchellingModel
from model_zoo.sir.model import Person, SIRModel

from abmforge import GridWorld, Scenario


class _NoOpScheduler:
    def step(self) -> None:
        pass


def _sir_model(
    *,
    seed: int = 42,
    **overrides: Any,
) -> SIRModel:
    parameters: dict[str, Any] = {
        "width": 8,
        "height": 8,
        "n_agents": 60,
        "initial_infected": 5,
        "infection_prob": 0.25,
        "recovery_prob": 0.10,
    }
    parameters.update(overrides)

    model = SIRModel(
        parameters=parameters,
        seed=seed,
    )
    model.setup()
    return model


def _schelling_model(
    *,
    seed: int = 42,
    **overrides: Any,
) -> SchellingModel:
    parameters: dict[str, Any] = {
        "width": 8,
        "height": 8,
        "density": 0.75,
        "homophily": 0.50,
    }
    parameters.update(overrides)

    model = SchellingModel(
        parameters=parameters,
        seed=seed,
    )
    model.setup()
    return model


def _sir_counts(
    model: SIRModel,
) -> tuple[int, int, int]:
    return (
        model.count_state("S"),
        model.count_state("I"),
        model.count_state("R"),
    )


def _sir_signature(
    model: SIRModel,
) -> tuple[tuple[Any, str, tuple[int, int]], ...]:
    assert isinstance(
        model.world,
        GridWorld,
    )

    return tuple(
        (
            agent.unique_id,
            cast(str, agent.state),
            model.world.position_of(agent),
        )
        for agent in model.agents
    )


def _schelling_positions(
    model: SchellingModel,
) -> dict[Any, tuple[int, int]]:
    assert isinstance(
        model.world,
        GridWorld,
    )

    return {agent.unique_id: model.world.position_of(agent) for agent in model.agents}


def _schelling_signature(
    model: SchellingModel,
) -> tuple[tuple[Any, int, bool, tuple[int, int]], ...]:
    assert isinstance(
        model.world,
        GridWorld,
    )

    return tuple(
        (
            agent.unique_id,
            cast(int, agent.group),
            cast(bool, agent.happy),
            model.world.position_of(agent),
        )
        for agent in model.agents
    )


def _metrics_by_step(
    records: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    metrics: dict[int, dict[str, Any]] = {}

    for record in records:
        step = int(record["step"])
        metric = str(record["metric"])

        metrics.setdefault(
            step,
            {},
        )[metric] = record["value"]

    return metrics


def _controlled_schelling_relocation() -> tuple[
    SchellingModel,
    Household,
    Household,
    Household,
]:
    model = _schelling_model(
        width=4,
        height=1,
        density=0.0,
        homophily=0.5,
    )

    assert isinstance(
        model.world,
        GridWorld,
    )

    target = model.agents.create(
        Household,
        n=1,
        group=0,
        happy=True,
    )[0]
    opposite = model.agents.create(
        Household,
        n=1,
        group=1,
        happy=True,
    )[0]
    same_group = model.agents.create(
        Household,
        n=1,
        group=0,
        happy=True,
    )[0]

    model.world.place(
        target,
        (0, 0),
    )
    model.world.place(
        opposite,
        (1, 0),
    )
    model.world.place(
        same_group,
        (2, 0),
    )

    return (
        model,
        target,
        opposite,
        same_group,
    )


def test_sir_conserves_population_and_transition_order() -> None:
    model = _sir_model(
        n_agents=80,
        initial_infected=6,
    )

    previous_s, _, previous_r = _sir_counts(model)
    previous_attack_rate = model.attack_rate()

    for _ in range(12):
        model.step()

        susceptible, infected, recovered = _sir_counts(model)

        states = {cast(str, agent.state) for agent in model.agents}

        assert states <= {
            "S",
            "I",
            "R",
        }
        assert susceptible >= 0
        assert infected >= 0
        assert recovered >= 0

        assert susceptible + infected + recovered == model.n_agents
        assert model.agents.count() == model.n_agents

        assert susceptible <= previous_s
        assert recovered >= previous_r

        assert model.attack_rate() == pytest.approx((infected + recovered) / model.n_agents)
        assert model.attack_rate() == pytest.approx(1.0 - susceptible / model.n_agents)
        assert model.attack_rate() >= previous_attack_rate

        previous_s = susceptible
        previous_r = recovered
        previous_attack_rate = model.attack_rate()


def test_sir_no_initial_infection_is_absorbing() -> None:
    model = _sir_model(
        n_agents=40,
        initial_infected=0,
        infection_prob=1.0,
        recovery_prob=1.0,
    )

    for _ in range(10):
        model.step()

    assert _sir_counts(model) == (
        40,
        0,
        0,
    )
    assert model.attack_rate() == 0.0


def test_sir_zero_infection_probability_prevents_new_cases() -> None:
    model = _sir_model(
        n_agents=50,
        initial_infected=7,
        infection_prob=0.0,
        recovery_prob=0.35,
    )

    initial_susceptible = 43
    initial_attack_rate = 7 / 50

    for _ in range(10):
        model.step()

        susceptible, _, _ = _sir_counts(model)

        assert susceptible == initial_susceptible
        assert model.attack_rate() == pytest.approx(initial_attack_rate)


def test_sir_zero_recovery_probability_prevents_recovery() -> None:
    model = _sir_model(
        n_agents=50,
        initial_infected=4,
        infection_prob=0.8,
        recovery_prob=0.0,
    )

    previous_infected = 4

    for _ in range(10):
        model.step()

        _, infected, recovered = _sir_counts(model)

        assert recovered == 0
        assert infected >= previous_infected

        previous_infected = infected


def test_sir_asynchronous_updates_allow_ordered_same_tick_cascade() -> None:
    model = _sir_model(
        width=4,
        height=1,
        n_agents=0,
        initial_infected=0,
        infection_prob=1.0,
        recovery_prob=0.0,
    )

    assert isinstance(
        model.world,
        GridWorld,
    )

    source = model.agents.create(
        Person,
        n=1,
        state="I",
    )[0]
    first_contact = model.agents.create(
        Person,
        n=1,
        state="S",
    )[0]
    second_contact = model.agents.create(
        Person,
        n=1,
        state="S",
    )[0]

    model.world.place(
        source,
        (0, 0),
    )
    model.world.place(
        first_contact,
        (1, 0),
    )
    model.world.place(
        second_contact,
        (2, 0),
    )

    source.step()

    assert first_contact.state == "I"
    assert second_contact.state == "S"

    first_contact.step()

    assert second_contact.state == "I"


def test_sir_all_infected_makes_infection_probability_irrelevant() -> None:
    no_transmission = _sir_model(
        seed=57,
        n_agents=36,
        initial_infected=36,
        infection_prob=0.0,
        recovery_prob=0.30,
    )
    certain_transmission = _sir_model(
        seed=57,
        n_agents=36,
        initial_infected=36,
        infection_prob=1.0,
        recovery_prob=0.30,
    )

    for _ in range(8):
        assert _sir_signature(no_transmission) == _sir_signature(certain_transmission)

        no_transmission.step()
        certain_transmission.step()

    assert _sir_signature(no_transmission) == _sir_signature(certain_transmission)


def test_sir_same_seed_reproduces_state_trajectory() -> None:
    first = _sir_model(
        seed=91,
    )
    second = _sir_model(
        seed=91,
    )

    for _ in range(10):
        assert _sir_signature(first) == _sir_signature(second)

        first.step()
        second.step()

    assert _sir_signature(first) == _sir_signature(second)


def test_sir_recorded_metrics_obey_scientific_invariants() -> None:
    result = Scenario(
        model=SIRModel,
        seed=73,
        steps=10,
        parameters={
            "width": 8,
            "height": 8,
            "n_agents": 60,
            "initial_infected": 5,
            "infection_prob": 0.30,
            "recovery_prob": 0.12,
        },
    ).run()

    metrics = _metrics_by_step(result.dataset.model_records)

    previous_susceptible = 60
    previous_recovered = 0
    previous_attack_rate = 0.0

    for step in sorted(metrics):
        values = metrics[step]

        susceptible = int(values["susceptible"])
        infected = int(values["infected"])
        recovered = int(values["recovered"])
        attack_rate = float(values["attack_rate"])

        assert susceptible + infected + recovered == 60
        assert susceptible <= previous_susceptible
        assert recovered >= previous_recovered
        assert attack_rate >= previous_attack_rate

        assert attack_rate == pytest.approx((infected + recovered) / 60)

        previous_susceptible = susceptible
        previous_recovered = recovered
        previous_attack_rate = attack_rate


def test_schelling_conserves_population_groups_and_vacancies() -> None:
    model = _schelling_model(
        width=9,
        height=7,
        density=0.70,
        homophily=0.55,
    )

    initial_ids = {agent.unique_id for agent in model.agents}
    initial_groups = Counter(cast(int, agent.group) for agent in model.agents)
    initial_empty = len(model.empty_cells())

    for _ in range(12):
        model.step()

        current_ids = {agent.unique_id for agent in model.agents}
        current_groups = Counter(cast(int, agent.group) for agent in model.agents)
        positions = list(_schelling_positions(model).values())
        empty_count = len(model.empty_cells())

        assert current_ids == initial_ids
        assert current_groups == initial_groups
        assert empty_count == initial_empty
        assert len(positions) == len(set(positions))
        assert model.agents.count() + empty_count == model.width * model.height

        assert 0.0 <= model.mean_similarity() <= 1.0
        assert 0 <= model.unhappy_count() <= model.agents.count()


def test_schelling_zero_density_boundary() -> None:
    model = _schelling_model(
        width=5,
        height=4,
        density=0.0,
        homophily=1.0,
    )

    assert model.agents.count() == 0
    assert len(model.empty_cells()) == 20
    assert model.mean_similarity() == 1.0
    assert model.unhappy_count() == 0

    for _ in range(3):
        model.step()

    assert model.agents.count() == 0
    assert len(model.empty_cells()) == 20


def test_schelling_single_group_configuration_is_absorbing() -> None:
    model = _schelling_model(
        density=0.70,
        homophily=1.0,
    )

    for agent in model.agents:
        agent.group = 0

    initial_positions = _schelling_positions(model)

    assert model.unhappy_count() == 0

    for _ in range(5):
        model.step()

    assert _schelling_positions(model) == initial_positions
    assert model.unhappy_count() == 0

    assert all(cast(bool, agent.happy) for agent in model.agents)


def test_schelling_group_label_swap_preserves_aggregate_state() -> None:
    model = _schelling_model(
        seed=101,
        homophily=0.60,
    )

    before_similarity = model.mean_similarity()
    before_unhappy = model.unhappy_count()
    before_agent_similarity = [cast(Household, agent).similarity() for agent in model.agents]

    for agent in model.agents:
        agent.group = 1 - agent.group

    after_agent_similarity = [cast(Household, agent).similarity() for agent in model.agents]

    assert model.mean_similarity() == pytest.approx(before_similarity)
    assert model.unhappy_count() == before_unhappy
    assert after_agent_similarity == before_agent_similarity


def test_schelling_unhappy_count_is_monotone_in_homophily() -> None:
    model = _schelling_model(
        seed=103,
    )

    counts: list[int] = []

    for threshold in [
        0.0,
        0.25,
        0.50,
        0.75,
        1.0,
    ]:
        model.homophily = threshold
        counts.append(model.unhappy_count())

    assert counts == sorted(counts)


def test_schelling_zero_homophily_prevents_relocation() -> None:
    model = _schelling_model(
        seed=107,
        homophily=0.0,
    )

    initial_positions = _schelling_positions(model)

    for _ in range(5):
        model.step()

    assert _schelling_positions(model) == initial_positions
    assert model.unhappy_count() == 0


def test_schelling_relocation_refreshes_mover_happy_state() -> None:
    model, target, _, _ = _controlled_schelling_relocation()

    assert isinstance(
        model.world,
        GridWorld,
    )
    assert target.similarity() == pytest.approx(0.0)

    target.step()

    assert model.world.position_of(target) == (
        3,
        0,
    )
    assert target.similarity() == pytest.approx(1.0)
    assert target.happy is True


def test_schelling_model_step_refreshes_final_happy_flags() -> None:
    model, _, _, _ = _controlled_schelling_relocation()

    for agent in model.agents:
        household = cast(
            Household,
            agent,
        )
        household.happy = not model.is_happy(household)

    model.scheduler = cast(
        Any,
        _NoOpScheduler(),
    )

    model.step()

    for agent in model.agents:
        household = cast(
            Household,
            agent,
        )

        assert household.happy is model.is_happy(household)


def test_schelling_same_seed_reproduces_state_trajectory() -> None:
    first = _schelling_model(
        seed=109,
    )
    second = _schelling_model(
        seed=109,
    )

    for _ in range(10):
        assert _schelling_signature(first) == _schelling_signature(second)

        first.step()
        second.step()

    assert _schelling_signature(first) == _schelling_signature(second)


def test_schelling_recorded_metrics_obey_invariants() -> None:
    width = 9
    height = 7

    result = Scenario(
        model=SchellingModel,
        seed=113,
        steps=10,
        parameters={
            "width": width,
            "height": height,
            "density": 0.70,
            "homophily": 0.55,
        },
    ).run()

    metrics = _metrics_by_step(result.dataset.model_records)

    expected_population = int(width * height * 0.70)
    expected_empty = width * height - expected_population

    for values in metrics.values():
        population = int(values["population"])
        empty_cells = int(values["empty_cells"])
        mean_similarity = float(values["mean_similarity"])
        unhappy = int(values["unhappy_households"])

        assert population == expected_population
        assert empty_cells == expected_empty
        assert population + empty_cells == width * height
        assert 0.0 <= mean_similarity <= 1.0
        assert 0 <= unhappy <= population
