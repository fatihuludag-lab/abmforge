from __future__ import annotations

from abmforge import Agent, GridWorld, Model, Scenario
from abmforge.scheduling import RandomActivation


class Person(Agent):
    """Person agent with SIR disease state."""

    def step(self) -> None:
        if self.state != "I":
            return

        for neighbor in self.neighbors(radius=1, include_center=False):
            if (
                neighbor.state == "S"
                and self.rng.random() < self.model.parameters["infection_prob"]
            ):
                neighbor.state = "I"

        if self.rng.random() < self.model.parameters["recovery_prob"]:
            self.state = "R"


class SIRModel(Model):
    """Simple spatial SIR epidemic model."""

    def setup(self) -> None:
        width = self.parameters.get("width", 30)
        height = self.parameters.get("height", 30)
        n_agents = self.parameters.get("n_agents", 300)
        initial_infected = self.parameters.get("initial_infected", 5)

        self.world = GridWorld(width=width, height=height, torus=True, multi=True)
        self.scheduler = RandomActivation(self)

        for i in range(n_agents):
            state = "I" if i < initial_infected else "S"
            agent = self.agents.create(Person, n=1, state=state)[0]
            position = (
                int(self.rng.integers(0, width)),
                int(self.rng.integers(0, height)),
            )
            self.world.place(agent, position)

        self.record.metric("susceptible", lambda model: model.count_state("S"))
        self.record.metric("infected", lambda model: model.count_state("I"))
        self.record.metric("recovered", lambda model: model.count_state("R"))

    def count_state(self, state: str) -> int:
        return sum(1 for agent in self.agents if agent.state == state)

    def step(self) -> None:
        self.scheduler.step()


if __name__ == "__main__":
    scenario = Scenario(
        model=SIRModel,
        seed=42,
        steps=100,
        parameters={
            "width": 30,
            "height": 30,
            "n_agents": 300,
            "initial_infected": 5,
            "infection_prob": 0.25,
            "recovery_prob": 0.05,
        },
    )

    result = scenario.run()
    result.dataset.write_csv("outputs/sir_epidemic")

    print("SIR epidemic model completed.")
    print(f"Run ID: {result.run_id}")
    print("CSV output written to outputs/sir_epidemic")
    print("Last model records:")
    for record in result.dataset.model_records[-9:]:
        print(record)
