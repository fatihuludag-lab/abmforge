from __future__ import annotations

from typing import cast

from abmforge import Agent, GridWorld, Model
from abmforge.scheduling import RandomActivation


class Person(Agent):
    """Person agent with a susceptible-infected-recovered disease state."""

    state: str

    def step(self) -> None:
        """Transmit infection to local neighbours and possibly recover."""
        if self.state != "I":
            return

        model = cast("SIRModel", self.model)

        for neighbour in self.neighbors(radius=1, include_center=False):
            if getattr(neighbour, "state", None) != "S":
                continue

            if self.rng.random() < model.infection_prob:
                neighbour.state = "I"

        if self.rng.random() < model.recovery_prob:
            self.state = "R"


class SIRModel(Model):
    """Spatial SIR epidemic model.

    The model demonstrates how local contacts can produce epidemic diffusion.
    It intentionally uses a simple asynchronous update rule for teaching.
    """

    width: int
    height: int
    n_agents: int
    initial_infected: int
    infection_prob: float
    recovery_prob: float
    scheduler: RandomActivation

    def setup(self) -> None:
        """Initialize spatial population, disease states, scheduler, and metrics."""
        self.width = int(self.parameters.get("width", 30))
        self.height = int(self.parameters.get("height", 30))
        self.n_agents = int(self.parameters.get("n_agents", 300))
        self.initial_infected = int(self.parameters.get("initial_infected", 5))
        self.infection_prob = float(self.parameters.get("infection_prob", 0.25))
        self.recovery_prob = float(self.parameters.get("recovery_prob", 0.05))

        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")

        if self.n_agents < 0:
            raise ValueError("n_agents must be non-negative")

        if self.initial_infected < 0:
            raise ValueError("initial_infected must be non-negative")

        if self.initial_infected > self.n_agents:
            raise ValueError("initial_infected must not exceed n_agents")

        if not 0.0 <= self.infection_prob <= 1.0:
            raise ValueError("infection_prob must be between 0 and 1")

        if not 0.0 <= self.recovery_prob <= 1.0:
            raise ValueError("recovery_prob must be between 0 and 1")

        self.world = GridWorld(
            width=self.width,
            height=self.height,
            torus=True,
            multi=True,
        )
        self.scheduler = RandomActivation(self)

        for index in range(self.n_agents):
            state = "I" if index < self.initial_infected else "S"
            person = self.agents.create(Person, n=1, state=state)[0]
            position = (
                int(self.rng.integers(0, self.width)),
                int(self.rng.integers(0, self.height)),
            )
            self.world.place(person, position)

        self.record.metric("susceptible", lambda model: model.count_state("S"))
        self.record.metric("infected", lambda model: model.count_state("I"))
        self.record.metric("recovered", lambda model: model.count_state("R"))
        self.record.metric("attack_rate", lambda model: model.attack_rate())
        self.record.agent("state")

    def step(self) -> None:
        """Advance the epidemic by one random-activation step."""
        self.scheduler.step()

    def count_state(self, state: str) -> int:
        """Return number of agents in a disease state."""
        return sum(1 for agent in self.agents if getattr(agent, "state", None) == state)

    def attack_rate(self) -> float:
        """Return share of agents that have ever been infected."""
        if self.n_agents == 0:
            return 0.0

        infected_or_recovered = self.count_state("I") + self.count_state("R")
        return infected_or_recovered / self.n_agents
