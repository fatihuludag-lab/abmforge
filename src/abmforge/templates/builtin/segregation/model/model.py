from __future__ import annotations

from statistics import fmean

from model.agents import Resident

from abmforge import GridWorld, Model
from abmforge.scheduling import StagedActivation


class SegregationTemplateModel(Model):
    """Minimal Schelling-style segregation model for researcher scaffolds."""

    def setup(self) -> None:
        self.width = int(self.parameters.get("width", 25))
        self.height = int(self.parameters.get("height", 25))
        self.density = float(self.parameters.get("density", 0.75))
        self.group_a_share = float(self.parameters.get("group_a_share", 0.50))
        self.homophily_threshold = float(self.parameters.get("homophily_threshold", 0.55))
        self.neighborhood_radius = int(self.parameters.get("neighborhood_radius", 1))

        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")

        if not 0.0 < self.density <= 1.0:
            raise ValueError("density must be greater than 0 and at most 1")

        if not 0.0 <= self.group_a_share <= 1.0:
            raise ValueError("group_a_share must be between 0 and 1")

        if not 0.0 <= self.homophily_threshold <= 1.0:
            raise ValueError("homophily_threshold must be between 0 and 1")

        if self.neighborhood_radius <= 0:
            raise ValueError("neighborhood_radius must be positive")

        self.capacity = self.width * self.height
        self.n_agents = round(self.capacity * self.density)

        if self.n_agents <= 0:
            raise ValueError("density creates zero agents")

        self.world = GridWorld(
            width=self.width,
            height=self.height,
            torus=True,
            multi=False,
        )
        self.scheduler = StagedActivation(
            self,
            stages=["evaluate", "relocate"],
            shuffle=True,
        )
        self.empty_positions: set[tuple[int, int]] = set()
        self.relocation_count = 0

        self._create_residents()
        self._register_recorders()

    def step(self) -> None:
        self.relocation_count = 0
        self.scheduler.step()

    def mean_similarity(self) -> float:
        values = [float(getattr(agent, "similarity", 1.0)) for agent in self.agents]
        return fmean(values) if values else 0.0

    def unhappy_agents(self) -> int:
        return sum(int(not bool(getattr(agent, "happy", True))) for agent in self.agents)

    def relocation_share(self) -> float:
        return self.relocation_count / len(self.agents) if self.agents else 0.0

    def _create_residents(self) -> None:
        group_a_count = round(self.n_agents * self.group_a_share)
        groups = ["A"] * group_a_count + ["B"] * (self.n_agents - group_a_count)
        group_order = self.rng.permutation(len(groups))
        groups = [groups[int(index)] for index in group_order]

        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        order = self.rng.permutation(len(positions))
        self.empty_positions = set(positions)

        residents = self.agents.create(
            Resident,
            n=self.n_agents,
            group="A",
            similarity=1.0,
            happy=True,
            will_relocate=False,
        )

        for resident, position_index, group in zip(
            residents,
            order[: self.n_agents],
            groups,
            strict=True,
        ):
            position = positions[int(position_index)]
            resident.group = group
            self.empty_positions.remove(position)
            self.world.place(resident, position)

    def _register_recorders(self) -> None:
        self.record.metric(
            "mean_similarity",
            lambda model: model.mean_similarity(),
        )
        self.record.metric(
            "unhappy_agents",
            lambda model: model.unhappy_agents(),
        )
        self.record.metric(
            "relocation_count",
            lambda model: model.relocation_count,
        )
        self.record.metric(
            "relocation_share",
            lambda model: model.relocation_share(),
        )
        self.record.metric(
            "segregation_index",
            lambda model: model.mean_similarity(),
        )
        self.record.agent(
            "group",
            when=lambda model: model.steps == 1,
            where=lambda agent: isinstance(agent, Resident),
        )
        self.record.agent(
            "similarity",
            every=5,
            where=lambda agent: isinstance(agent, Resident),
        )
        self.record.agent(
            "happy",
            every=5,
            where=lambda agent: isinstance(agent, Resident),
        )
