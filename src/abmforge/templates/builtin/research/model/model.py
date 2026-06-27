from __future__ import annotations

from typing import cast

from model.agents import ResearchAgent

from abmforge import Model
from abmforge.scheduling import RandomActivation


class ResearchStudyModel(Model):
    """Minimal threshold-adoption model for reproducible research scaffolds."""

    def setup(self) -> None:
        self.population = int(self.parameters.get("population", 80))
        self.initial_adoption_share = float(self.parameters.get("initial_adoption_share", 0.10))
        self.base_threshold = float(self.parameters.get("base_threshold", 0.35))
        self.threshold_sd = float(self.parameters.get("threshold_sd", 0.08))
        self.peer_influence = float(self.parameters.get("peer_influence", 0.70))
        self.external_influence = float(self.parameters.get("external_influence", 0.05))

        self._validate_parameters()

        self.scheduler = RandomActivation(self)
        self.new_adoptions = 0
        self.current_adoption_share = 0.0

        agents = self.agents.create(
            ResearchAgent,
            n=self.population,
            adopted=False,
            threshold=self.base_threshold,
        )

        for agent in agents:
            sampled_threshold = self.base_threshold + float(self.rng.normal(0.0, self.threshold_sd))
            agent.threshold = min(1.0, max(0.0, sampled_threshold))

        initial_count = round(self.population * self.initial_adoption_share)
        initial_count = min(self.population, max(0, int(initial_count)))

        if initial_count:
            order = self.rng.permutation(len(agents))
            for index in order[:initial_count]:
                cast(ResearchAgent, agents[int(index)]).adopted = True

        self.current_adoption_share = self._adoption_share()

        self.record.metric(
            "adopter_count",
            lambda model: model.agents.count_where(adopted=True),
        )
        self.record.metric(
            "adoption_share",
            lambda model: model._adoption_share(),
        )
        self.record.metric(
            "new_adoptions",
            lambda model: model.new_adoptions,
        )
        self.record.metric(
            "mean_threshold",
            lambda model: model.agents.mean("threshold"),
        )

        self.record.agent(
            "adopted",
            every=5,
            where=lambda agent: isinstance(agent, ResearchAgent),
        )
        self.record.agent(
            "threshold",
            every=5,
            where=lambda agent: isinstance(agent, ResearchAgent),
        )

    def step(self) -> None:
        self.new_adoptions = 0
        self.current_adoption_share = self._adoption_share()
        self.scheduler.step()
        self.current_adoption_share = self._adoption_share()

    def _adoption_share(self) -> float:
        if self.population == 0:
            return 0.0
        return self.agents.count_where(adopted=True) / self.population

    def _validate_parameters(self) -> None:
        if self.population <= 0:
            raise ValueError("population must be positive")

        for name in [
            "initial_adoption_share",
            "base_threshold",
            "peer_influence",
            "external_influence",
        ]:
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")

        if self.threshold_sd < 0.0:
            raise ValueError("threshold_sd must be non-negative")
