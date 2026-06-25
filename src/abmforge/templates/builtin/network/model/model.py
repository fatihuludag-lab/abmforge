from __future__ import annotations

from model.agents import NetworkResident

from abmforge import Model, NetworkSpace
from abmforge.scheduling import StagedActivation


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


class NetworkTemplateModel(Model):
    """Minimal network diffusion model for researcher project scaffolds."""

    def setup(self) -> None:
        self.n_agents = int(self.parameters.get("n_agents", 80))
        self.initial_adoption_share = float(self.parameters.get("initial_adoption_share", 0.10))
        self.threshold_mean = float(self.parameters.get("threshold_mean", 0.35))
        self.threshold_sd = float(self.parameters.get("threshold_sd", 0.10))
        self.shortcut_probability = float(self.parameters.get("shortcut_probability", 0.04))
        self.broadcast_probability = float(self.parameters.get("broadcast_probability", 0.01))

        if self.n_agents <= 0:
            raise ValueError("n_agents must be positive")

        if not 0.0 <= self.initial_adoption_share <= 1.0:
            raise ValueError("initial_adoption_share must be between 0 and 1")

        if self.threshold_sd < 0.0:
            raise ValueError("threshold_sd must be non-negative")

        if not 0.0 <= self.shortcut_probability <= 1.0:
            raise ValueError("shortcut_probability must be between 0 and 1")

        if not 0.0 <= self.broadcast_probability <= 1.0:
            raise ValueError("broadcast_probability must be between 0 and 1")

        self.world = NetworkSpace()
        self.scheduler = StagedActivation(
            self,
            stages=["decide", "adopt"],
            shuffle=True,
        )

        self._create_network()
        self._create_agents()
        self._register_recorders()

    def step(self) -> None:
        self.scheduler.step()

    def adopted_count(self) -> int:
        return sum(int(getattr(agent, "adopted", False)) for agent in self.agents)

    def adoption_rate(self) -> float:
        return self.adopted_count() / len(self.agents) if self.agents else 0.0

    def average_degree(self) -> float:
        return sum(self.world.degree(node_id) for node_id in range(self.n_agents)) / self.n_agents

    def _create_network(self) -> None:
        for node_id in range(self.n_agents):
            self.world.add_node(node_id)

        # Ring backbone.
        for node_id in range(self.n_agents):
            self.world.add_edge(node_id, (node_id + 1) % self.n_agents)

        # Optional random shortcuts.
        for source in range(self.n_agents):
            for target in range(source + 2, self.n_agents):
                if source == 0 and target == self.n_agents - 1:
                    continue

                if self.rng.random() < self.shortcut_probability:
                    self.world.add_edge(source, target)

    def _create_agents(self) -> None:
        initial_count = round(self.n_agents * self.initial_adoption_share)
        initial_adopters = set(
            int(index)
            for index in self.rng.choice(
                self.n_agents,
                size=initial_count,
                replace=False,
            )
        )

        for node_id in range(self.n_agents):
            threshold = _clamp(
                float(self.rng.normal(self.threshold_mean, self.threshold_sd)),
                0.0,
                1.0,
            )
            adopted = node_id in initial_adopters
            agent = self.agents.create(
                NetworkResident,
                n=1,
                threshold=threshold,
                adopted=adopted,
                will_adopt=adopted,
            )[0]
            self.world.place(agent, node_id)

    def _register_recorders(self) -> None:
        self.record.metric(
            "adopted_count",
            lambda model: model.adopted_count(),
        )
        self.record.metric(
            "adoption_rate",
            lambda model: model.adoption_rate(),
        )
        self.record.metric(
            "average_degree",
            lambda model: model.average_degree(),
        )
        self.record.agent(
            "adopted",
            every=5,
            where=lambda agent: isinstance(agent, NetworkResident),
        )
        self.record.agent(
            "threshold",
            when=lambda model: model.steps == 1,
            where=lambda agent: isinstance(agent, NetworkResident),
        )
