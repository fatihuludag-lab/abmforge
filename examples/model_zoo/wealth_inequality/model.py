from __future__ import annotations

from abmforge import Agent, Model


class WealthAgent(Agent):
    """Agent with integer wealth."""

    def step(self) -> None:
        self.model.transfer_wealth(self)


class WealthInequalityModel(Model):
    """Simple stochastic wealth-transfer model."""

    def setup(self) -> None:
        self.population = int(self.parameters.get("population", 80))
        self.initial_wealth = int(self.parameters.get("initial_wealth", 10))
        self.transfer_probability = float(self.parameters.get("transfer_probability", 0.65))
        self.transfer_amount = int(self.parameters.get("transfer_amount", 1))
        self.income_probability = float(self.parameters.get("income_probability", 0.15))
        self.income_amount = int(self.parameters.get("income_amount", 1))

        self._validate_parameters()

        self.people = list(
            self.agents.create(
                WealthAgent,
                n=self.population,
                wealth=self.initial_wealth,
            )
        )

        self.record.metric("gini", lambda model: model.gini())
        self.record.metric("mean_wealth", lambda model: model.mean_wealth())
        self.record.metric("max_wealth", lambda model: model.max_wealth())
        self.record.metric("total_wealth", lambda model: model.total_wealth())
        self.record.agent(
            "wealth",
            every=5,
            where=lambda agent: isinstance(agent, WealthAgent),
        )

    def step(self) -> None:
        order = self.rng.permutation(len(self.people))
        for index in order:
            self.people[int(index)].step()

    def transfer_wealth(self, donor: WealthAgent) -> None:
        if float(self.rng.random()) < self.income_probability:
            donor.wealth += self.income_amount

        if donor.wealth < self.transfer_amount:
            return

        if float(self.rng.random()) >= self.transfer_probability:
            return

        receiver_index = int(self.rng.integers(0, len(self.people)))
        receiver = self.people[receiver_index]

        if receiver is donor and len(self.people) > 1:
            receiver = self.people[(receiver_index + 1) % len(self.people)]

        donor.wealth -= self.transfer_amount
        receiver.wealth += self.transfer_amount

    def total_wealth(self) -> float:
        return float(sum(agent.wealth for agent in self.people))

    def mean_wealth(self) -> float:
        return self.total_wealth() / self.population

    def max_wealth(self) -> float:
        return float(max(agent.wealth for agent in self.people))

    def gini(self) -> float:
        wealth = sorted(float(agent.wealth) for agent in self.people)
        total = sum(wealth)

        if total == 0.0:
            return 0.0

        n = len(wealth)
        weighted_sum = sum((index + 1) * value for index, value in enumerate(wealth))
        return (2.0 * weighted_sum) / (n * total) - (n + 1.0) / n

    def _validate_parameters(self) -> None:
        if self.population <= 1:
            raise ValueError("population must be greater than 1")

        if self.initial_wealth < 0:
            raise ValueError("initial_wealth must be non-negative")

        if self.transfer_amount <= 0:
            raise ValueError("transfer_amount must be positive")

        if self.income_amount < 0:
            raise ValueError("income_amount must be non-negative")

        for name in ["transfer_probability", "income_probability"]:
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
