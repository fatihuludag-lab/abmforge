from __future__ import annotations

from typing import cast

from abmforge import Agent, GridWorld, Model
from abmforge.scheduling import RandomActivation


class Household(Agent):
    """Household agent in a Schelling-style segregation model."""

    group: int
    happy: bool

    def similarity(self) -> float | None:
        """Return the share of neighbours from the same group.

        Returns None when the household has no neighbours.
        """
        neighbours = self.neighbors(radius=1, include_center=False)

        if not neighbours:
            return None

        same_group = sum(
            1 for neighbour in neighbours if getattr(neighbour, "group", None) == self.group
        )
        return same_group / len(neighbours)

    def step(self) -> None:
        """Evaluate local satisfaction and move if unhappy."""
        model = cast("SchellingModel", self.model)
        similarity = self.similarity()

        self.happy = similarity is None or similarity >= model.homophily

        if not self.happy:
            model.move_to_random_empty_cell(self)


class SchellingModel(Model):
    """Schelling segregation model.

    The model demonstrates how local homophily preferences can generate
    emergent macro-level spatial segregation.
    """

    width: int
    height: int
    density: float
    homophily: float
    scheduler: RandomActivation

    def setup(self) -> None:
        """Initialize grid, households, scheduler, and recorded metrics."""
        self.width = int(self.parameters.get("width", 20))
        self.height = int(self.parameters.get("height", 20))
        self.density = float(self.parameters.get("density", 0.8))
        self.homophily = float(self.parameters.get("homophily", 0.5))

        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")

        if not 0.0 <= self.density <= 1.0:
            raise ValueError("density must be between 0 and 1")

        if not 0.0 <= self.homophily <= 1.0:
            raise ValueError("homophily must be between 0 and 1")

        self.world = GridWorld(
            width=self.width,
            height=self.height,
            torus=True,
            multi=False,
        )
        self.scheduler = RandomActivation(self)

        cells = [(x, y) for x in range(self.width) for y in range(self.height)]
        n_agents = int(len(cells) * self.density)
        positions = self.rng.permutation(len(cells))[:n_agents]

        for position_index in positions:
            group = int(self.rng.integers(0, 2))
            household = self.agents.create(Household, n=1, group=group, happy=True)[0]
            self.world.place(household, cells[int(position_index)])

        self.record.metric("population", lambda model: model.agents.count())
        self.record.metric("empty_cells", lambda model: len(model.empty_cells()))
        self.record.metric("mean_similarity", lambda model: model.mean_similarity())
        self.record.metric("unhappy_households", lambda model: model.unhappy_count())
        self.record.agent("group")
        self.record.agent("happy")

    def step(self) -> None:
        """Advance the model by one random-activation step."""
        self.scheduler.step()

    def empty_cells(self) -> list[tuple[int, int]]:
        """Return all empty grid cells."""
        assert isinstance(self.world, GridWorld)

        cells: list[tuple[int, int]] = []

        for x in range(self.width):
            for y in range(self.height):
                position = (x, y)
                if self.world.is_empty(position):
                    cells.append(position)

        return cells

    def move_to_random_empty_cell(self, household: Household) -> None:
        """Move a household to a random empty cell when possible."""
        assert isinstance(self.world, GridWorld)

        empty_cells = self.empty_cells()

        if not empty_cells:
            return

        index = int(self.rng.integers(0, len(empty_cells)))
        self.world.move(household, empty_cells[index])

    def is_happy(self, household: Household) -> bool:
        """Return whether a household is satisfied in its current neighbourhood."""
        similarity = household.similarity()
        return similarity is None or similarity >= self.homophily

    def unhappy_count(self) -> int:
        """Return number of currently unhappy households."""
        return sum(
            1 for agent in self.agents if isinstance(agent, Household) and not self.is_happy(agent)
        )

    def mean_similarity(self) -> float:
        """Return mean local similarity over households with neighbours."""
        similarities: list[float] = []

        for agent in self.agents:
            if not isinstance(agent, Household):
                continue

            similarity = agent.similarity()
            if similarity is not None:
                similarities.append(similarity)

        if not similarities:
            return 1.0

        return float(sum(similarities) / len(similarities))
