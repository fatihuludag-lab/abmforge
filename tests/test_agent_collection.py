from __future__ import annotations

from abmforge import Agent, Model


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


def test_create_count_and_aggregate() -> None:
    model = Model(seed=42)
    created = model.agents.create(Person, n=4, wealth=2)

    assert len(created) == 4
    assert model.agents.count() == 4
    assert model.agents.sum("wealth") == 8.0
    assert model.agents.mean("wealth") == 2.0


def test_shuffle_do_is_seed_deterministic() -> None:
    class OrderAgent(Agent):
        def step(self) -> None:
            self.model.order.append(self.unique_id)

    def run_once() -> list[int | str]:
        model = Model(seed=123)
        model.order = []
        model.agents.create(OrderAgent, n=5)
        model.agents.shuffle_do("step")
        return model.order

    assert run_once() == run_once()


def test_where_and_count_where() -> None:
    model = Model(seed=42)
    model.agents.create(Person, n=2, wealth=1, state="a")
    model.agents.create(Person, n=3, wealth=2, state="b")

    assert len(model.agents.where(state="a")) == 2
    assert model.agents.count_where(state="b") == 3
