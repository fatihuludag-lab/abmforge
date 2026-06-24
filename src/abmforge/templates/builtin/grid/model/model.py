from __future__ import annotations

from model.agents import Resident

from abmforge import GridWorld, Model
from abmforge.scheduling import RandomActivation


class GridTemplateModel(Model):
    """Minimal grid-based ABMForge model for researcher project scaffolds."""

    def setup(self) -> None:
        self.width = int(self.parameters.get("width", 20))
        self.height = int(self.parameters.get("height", 20))
        self.n_agents = int(self.parameters.get("n_agents", 100))
        self.initial_wealth = int(self.parameters.get("initial_wealth", 10))
        self.transfer_probability = float(self.parameters.get("transfer_probability", 0.35))

        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")

        if self.n_agents < 0:
            raise ValueError("n_agents must be non-negative")

        if self.n_agents > self.width * self.height:
            raise ValueError("n_agents cannot exceed the number of grid cells when multi=False")

        if not 0.0 <= self.transfer_probability <= 1.0:
            raise ValueError("transfer_probability must be between 0 and 1")

        self.world = GridWorld(
            width=self.width,
            height=self.height,
            torus=True,
            multi=False,
        )
        self.scheduler = RandomActivation(self)

        agents = self.agents.create(
            Resident,
            n=self.n_agents,
            wealth=self.initial_wealth,
        )

        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        order = self.rng.permutation(len(positions))

        for agent, position_index in zip(agents, order[: self.n_agents], strict=True):
            self.world.place(agent, positions[int(position_index)])

        self.record.metric(
            "total_wealth",
            lambda model: model.agents.sum("wealth"),
        )
        self.record.metric(
            "mean_wealth",
            lambda model: model.agents.mean("wealth"),
        )
        self.record.metric(
            "occupied_cells",
            lambda model: len(model.agents),
        )
        self.record.agent(
            "wealth",
            every=5,
            where=lambda agent: isinstance(agent, Resident),
        )

    def step(self) -> None:
        self.scheduler.step()
