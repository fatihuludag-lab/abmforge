from __future__ import annotations

from statistics import fmean

from model.agents import Forager

from abmforge import GridWorld, Model
from abmforge.scheduling import RandomActivation


class ResourceTemplateModel(Model):
    """Minimal renewable-resource competition model for researcher scaffolds."""

    def setup(self) -> None:
        self.width = int(self.parameters.get("width", 25))
        self.height = int(self.parameters.get("height", 25))
        self.n_agents = int(self.parameters.get("n_agents", 120))
        self.initial_resource_mean = float(self.parameters.get("initial_resource_mean", 6.0))
        self.resource_capacity = float(self.parameters.get("resource_capacity", 12.0))
        self.resource_regrowth = float(self.parameters.get("resource_regrowth", 0.35))
        self.harvest_rate = float(self.parameters.get("harvest_rate", 4.0))
        self.energy_from_resource = float(self.parameters.get("energy_from_resource", 1.0))
        self.metabolism = float(self.parameters.get("metabolism", 1.2))
        self.initial_energy = float(self.parameters.get("initial_energy", 8.0))
        self.vision_radius = int(self.parameters.get("vision_radius", 2))

        self._validate_parameters()

        self.world = GridWorld(
            width=self.width,
            height=self.height,
            torus=True,
            multi=False,
        )
        self.scheduler = RandomActivation(self)
        self.resource: dict[tuple[int, int], float] = {}
        self.empty_positions: set[tuple[int, int]] = set()
        self.total_harvested = 0.0

        self._create_resource_field()
        self._create_foragers()
        self._register_recorders()

    def step(self) -> None:
        self.total_harvested = 0.0
        self.scheduler.step()
        self._regrow_resources()

    def best_visible_position(self, current: tuple[int, int]) -> tuple[int, int]:
        candidates = [
            position
            for position in self.visible_positions(current)
            if position == current or position in self.empty_positions
        ]

        if not candidates:
            return current

        return max(
            candidates,
            key=lambda position: (
                self.resource.get(position, 0.0),
                float(self.rng.random()),
            ),
        )

    def visible_positions(self, current: tuple[int, int]) -> list[tuple[int, int]]:
        x0, y0 = current
        positions: list[tuple[int, int]] = []

        for dx in range(-self.vision_radius, self.vision_radius + 1):
            for dy in range(-self.vision_radius, self.vision_radius + 1):
                x = (x0 + dx) % self.width
                y = (y0 + dy) % self.height
                positions.append((x, y))

        return positions

    def harvest_at(self, position: tuple[int, int]) -> float:
        available = self.resource.get(position, 0.0)
        harvested = min(available, self.harvest_rate)
        self.resource[position] = available - harvested
        self.total_harvested += harvested
        return harvested

    def active_agents(self) -> int:
        return sum(int(bool(getattr(agent, "active", False))) for agent in self.agents)

    def mean_wealth(self) -> float:
        values = [float(getattr(agent, "wealth", 0.0)) for agent in self.agents]
        return fmean(values) if values else 0.0

    def gini_wealth(self) -> float:
        values = sorted(float(getattr(agent, "wealth", 0.0)) for agent in self.agents)
        if not values or sum(values) == 0.0:
            return 0.0

        n = len(values)
        weighted_sum = sum((index + 1) * value for index, value in enumerate(values))
        return (2.0 * weighted_sum) / (n * sum(values)) - (n + 1.0) / n

    def total_resource(self) -> float:
        return sum(self.resource.values())

    def depleted_cells(self) -> int:
        return sum(int(value <= 0.01) for value in self.resource.values())

    def depletion_rate(self) -> float:
        return self.depleted_cells() / len(self.resource) if self.resource else 0.0

    def _validate_parameters(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")

        if self.n_agents <= 0:
            raise ValueError("n_agents must be positive")

        if self.n_agents > self.width * self.height:
            raise ValueError("n_agents cannot exceed the number of grid cells when multi=False")

        if self.initial_resource_mean < 0.0:
            raise ValueError("initial_resource_mean must be non-negative")

        if self.resource_capacity <= 0.0:
            raise ValueError("resource_capacity must be positive")

        if not 0.0 <= self.resource_regrowth <= 1.0:
            raise ValueError("resource_regrowth must be between 0 and 1")

        if self.harvest_rate < 0.0:
            raise ValueError("harvest_rate must be non-negative")

        if self.energy_from_resource < 0.0:
            raise ValueError("energy_from_resource must be non-negative")

        if self.metabolism < 0.0:
            raise ValueError("metabolism must be non-negative")

        if self.initial_energy <= 0.0:
            raise ValueError("initial_energy must be positive")

        if self.vision_radius <= 0:
            raise ValueError("vision_radius must be positive")

    def _create_resource_field(self) -> None:
        for x in range(self.width):
            for y in range(self.height):
                value = float(
                    self.rng.normal(
                        self.initial_resource_mean,
                        self.initial_resource_mean / 4.0,
                    )
                )
                self.resource[(x, y)] = min(
                    self.resource_capacity,
                    max(0.0, value),
                )

    def _create_foragers(self) -> None:
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        order = self.rng.permutation(len(positions))
        self.empty_positions = set(positions)

        for forager_id in range(self.n_agents):
            forager = self.agents.create(
                Forager,
                n=1,
                energy=self.initial_energy,
                wealth=0.0,
                active=True,
            )[0]
            position = positions[int(order[forager_id])]
            self.empty_positions.remove(position)
            self.world.place(forager, position)

    def _regrow_resources(self) -> None:
        for position, value in list(self.resource.items()):
            gap = self.resource_capacity - value
            self.resource[position] = min(
                self.resource_capacity,
                value + self.resource_regrowth * gap,
            )

    def _register_recorders(self) -> None:
        self.record.metric(
            "mean_wealth",
            lambda model: model.mean_wealth(),
        )
        self.record.metric(
            "gini_wealth",
            lambda model: model.gini_wealth(),
        )
        self.record.metric(
            "active_agents",
            lambda model: model.active_agents(),
        )
        self.record.metric(
            "total_resource",
            lambda model: model.total_resource(),
        )
        self.record.metric(
            "total_harvested",
            lambda model: model.total_harvested,
        )
        self.record.metric(
            "depleted_cells",
            lambda model: model.depleted_cells(),
        )
        self.record.metric(
            "depletion_rate",
            lambda model: model.depletion_rate(),
        )
        self.record.agent(
            "wealth",
            every=10,
            where=lambda agent: isinstance(agent, Forager),
        )
        self.record.agent(
            "energy",
            every=10,
            where=lambda agent: isinstance(agent, Forager),
        )
        self.record.agent(
            "active",
            every=10,
            where=lambda agent: isinstance(agent, Forager),
        )
