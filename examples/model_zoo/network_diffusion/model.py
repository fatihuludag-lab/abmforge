from __future__ import annotations

from abmforge import Agent, Model


class DiffusionAgent(Agent):
    """Agent with adoption state and adoption threshold."""


class NetworkDiffusionModel(Model):
    """Threshold diffusion on a deterministic ring network."""

    def setup(self) -> None:
        self.population = int(self.parameters.get("population", 90))
        self.initial_adoption_share = float(self.parameters.get("initial_adoption_share", 0.08))
        self.network_radius = int(self.parameters.get("network_radius", 2))
        self.peer_influence = float(self.parameters.get("peer_influence", 0.85))
        self.external_influence = float(self.parameters.get("external_influence", 0.04))
        self.base_threshold = float(self.parameters.get("base_threshold", 0.35))
        self.threshold_sd = float(self.parameters.get("threshold_sd", 0.07))

        self._validate_parameters()

        self.nodes = list(
            self.agents.create(
                DiffusionAgent,
                n=self.population,
                adopted=False,
                threshold=self.base_threshold,
            )
        )
        for index, agent in enumerate(self.nodes):
            agent.node_id = index
            threshold = self.base_threshold + float(self.rng.normal(0.0, self.threshold_sd))
            agent.threshold = min(1.0, max(0.0, threshold))

        initial_count = max(1, round(self.population * self.initial_adoption_share))
        seed_nodes = self.rng.choice(self.population, size=initial_count, replace=False)
        for index in seed_nodes:
            self.nodes[int(index)].adopted = True

        self.adjacency = self._ring_adjacency()
        self.new_adoptions = 0

        self.record.metric("adoption_share", lambda model: model.adoption_share())
        self.record.metric("adopter_count", lambda model: model.adopter_count())
        self.record.metric("new_adoptions", lambda model: model.new_adoptions)
        self.record.metric("mean_threshold", lambda model: model.mean_threshold())
        self.record.agent(
            "adopted",
            every=5,
            where=lambda agent: isinstance(agent, DiffusionAgent),
        )
        self.record.agent(
            "threshold",
            every=5,
            where=lambda agent: isinstance(agent, DiffusionAgent),
        )

    def step(self) -> None:
        newly_adopted: list[DiffusionAgent] = []

        for agent in self.nodes:
            if agent.adopted:
                continue

            exposure = self._neighbor_adoption_share(agent.node_id)
            pressure = self.external_influence + self.peer_influence * exposure

            if pressure >= agent.threshold:
                newly_adopted.append(agent)

        for agent in newly_adopted:
            agent.adopted = True

        self.new_adoptions = len(newly_adopted)

    def adoption_share(self) -> float:
        return self.adopter_count() / self.population

    def adopter_count(self) -> int:
        return sum(1 for agent in self.nodes if agent.adopted)

    def mean_threshold(self) -> float:
        return sum(float(agent.threshold) for agent in self.nodes) / self.population

    def _neighbor_adoption_share(self, node_id: int) -> float:
        neighbors = self.adjacency[node_id]
        if not neighbors:
            return 0.0
        adopted = sum(1 for index in neighbors if self.nodes[index].adopted)
        return adopted / len(neighbors)

    def _ring_adjacency(self) -> dict[int, list[int]]:
        adjacency: dict[int, list[int]] = {}

        for node_id in range(self.population):
            neighbors: list[int] = []
            for offset in range(1, self.network_radius + 1):
                neighbors.append((node_id - offset) % self.population)
                neighbors.append((node_id + offset) % self.population)
            adjacency[node_id] = sorted(set(neighbors))

        return adjacency

    def _validate_parameters(self) -> None:
        if self.population <= 2:
            raise ValueError("population must be greater than 2")

        if self.network_radius <= 0:
            raise ValueError("network_radius must be positive")

        if self.network_radius >= self.population:
            raise ValueError("network_radius must be smaller than population")

        if self.threshold_sd < 0.0:
            raise ValueError("threshold_sd must be non-negative")

        for name in [
            "initial_adoption_share",
            "peer_influence",
            "external_influence",
            "base_threshold",
        ]:
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
