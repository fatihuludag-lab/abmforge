from __future__ import annotations

from abmforge import Agent, GridWorld, Model, Scenario
from abmforge.scheduling import RandomActivation


class SugarAgent(Agent):
    def step(self) -> None:
        best_position = self.pos
        best_sugar = self.model.sugar_map[self.pos]

        x, y = self.pos

        for dx in range(-self.vision, self.vision + 1):
            for dy in range(-self.vision, self.vision + 1):
                try:
                    position = self.model.world.normalize((x + dx, y + dy))
                except ValueError:
                    continue

                sugar = self.model.sugar_map[position]

                if sugar > best_sugar:
                    best_sugar = sugar
                    best_position = position

        self.model.world.move(self, best_position)

        self.wealth += self.model.sugar_map[best_position]
        self.model.sugar_map[best_position] = 0


class SugarscapeModel(Model):
    def setup(self) -> None:
        width = self.parameters.get("width", 25)
        height = self.parameters.get("height", 25)

        self.world = GridWorld(
            width=width,
            height=height,
            torus=False,
            multi=True,
        )

        self.scheduler = RandomActivation(self)

        self.sugar_map = {}

        for x in range(width):
            for y in range(height):
                distance = abs(x - width // 2) + abs(y - height // 2)
                sugar = max(0, 8 - distance // 2)
                self.sugar_map[(x, y)] = sugar

        n_agents = self.parameters.get("n_agents", 100)

        for _ in range(n_agents):
            agent = self.agents.create(
                SugarAgent,
                n=1,
                wealth=0,
                vision=2,
            )[0]

            position = (
                int(self.rng.integers(0, width)),
                int(self.rng.integers(0, height)),
            )

            self.world.place(agent, position)

        self.record.metric(
            "total_wealth",
            lambda model: model.total_wealth(),
        )

        self.record.metric(
            "mean_wealth",
            lambda model: model.mean_wealth(),
        )

    def total_wealth(self) -> float:
        return sum(agent.wealth for agent in self.agents)

    def mean_wealth(self) -> float:
        values = [agent.wealth for agent in self.agents]

        if not values:
            return 0.0

        return sum(values) / len(values)

    def regrow_sugar(self) -> None:
        for position in self.sugar_map:
            self.sugar_map[position] = min(
                self.sugar_map[position] + 1,
                8,
            )

    def step(self) -> None:
        self.scheduler.step()
        self.regrow_sugar()


if __name__ == "__main__":
    scenario = Scenario(
        model=SugarscapeModel,
        seed=42,
        steps=50,
        parameters={
            "width": 25,
            "height": 25,
            "n_agents": 100,
        },
    )

    result = scenario.run()

    result.dataset.write_csv("outputs/sugarscape")

    print("Sugarscape completed")
    print(result.dataset.model_records[-5:])
