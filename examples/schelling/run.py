from __future__ import annotations

from abmforge import Agent, GridWorld, Model, Scenario
from abmforge.scheduling import RandomActivation


class Household(Agent):
    """Household agent in a Schelling segregation model."""

    def step(self) -> None:
        neighbors = self.neighbors(radius=1, include_center=False)

        if not neighbors:
            return

        same_group = sum(1 for neighbor in neighbors if neighbor.group == self.group)
        similarity = same_group / len(neighbors)

        if similarity < self.model.parameters["homophily"]:
            empty_cells = self.model.empty_cells()
            if empty_cells:
                idx = int(self.rng.integers(0, len(empty_cells)))
                self.model.world.move(self, empty_cells[idx])


class SchellingModel(Model):
    """Classic Schelling segregation model."""

    def setup(self) -> None:
        width = self.parameters.get("width", 20)
        height = self.parameters.get("height", 20)
        density = self.parameters.get("density", 0.8)

        self.world = GridWorld(width=width, height=height, torus=True, multi=False)
        self.scheduler = RandomActivation(self)

        n_cells = width * height
        n_agents = int(n_cells * density)

        for _ in range(n_agents):
            group = int(self.rng.integers(0, 2))
            agent = self.agents.create(Household, n=1, group=group)[0]
            empty_cells = self.empty_cells()
            idx = int(self.rng.integers(0, len(empty_cells)))
            self.world.place(agent, empty_cells[idx])

        self.record.metric("mean_similarity", lambda model: model.mean_similarity())
        self.record.metric("empty_cells", lambda model: len(model.empty_cells()))

    def empty_cells(self) -> list[tuple[int, int]]:
        cells = []
        for x in range(self.world.width):
            for y in range(self.world.height):
                position = (x, y)
                if self.world.is_empty(position):
                    cells.append(position)
        return cells

    def mean_similarity(self) -> float:
        similarities = []

        for agent in self.agents:
            neighbors = self.world.neighbors(agent, radius=1, include_center=False)
            if not neighbors:
                continue

            same_group = sum(1 for neighbor in neighbors if neighbor.group == agent.group)
            similarities.append(same_group / len(neighbors))

        if not similarities:
            return 0.0

        return sum(similarities) / len(similarities)

    def step(self) -> None:
        self.scheduler.step()


if __name__ == "__main__":
    scenario = Scenario(
        model=SchellingModel,
        seed=42,
        steps=50,
        parameters={
            "width": 20,
            "height": 20,
            "density": 0.8,
            "homophily": 0.5,
        },
    )

    result = scenario.run()
    result.dataset.write_csv("outputs/schelling")

    print("Schelling model completed.")
    print(f"Run ID: {result.run_id}")
    print("CSV output written to outputs/schelling")
    print("Last model records:")
    for record in result.dataset.model_records[-5:]:
        print(record)
