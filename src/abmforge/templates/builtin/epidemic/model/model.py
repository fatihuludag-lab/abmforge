from __future__ import annotations

from model.agents import Person

from abmforge import GridWorld, Model
from abmforge.scheduling import StagedActivation


class EpidemicTemplateModel(Model):
    """Minimal spatial SIR model for researcher project scaffolds."""

    def setup(self) -> None:
        self.width = int(self.parameters.get("width", 25))
        self.height = int(self.parameters.get("height", 25))
        self.n_agents = int(self.parameters.get("n_agents", 300))
        self.initial_infected_share = float(self.parameters.get("initial_infected_share", 0.03))
        self.infection_probability = float(self.parameters.get("infection_probability", 0.06))
        self.recovery_probability = float(self.parameters.get("recovery_probability", 0.08))
        self.contact_radius = int(self.parameters.get("contact_radius", 1))

        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")

        if self.n_agents <= 0:
            raise ValueError("n_agents must be positive")

        if self.n_agents > self.width * self.height:
            raise ValueError("n_agents cannot exceed the number of grid cells when multi=False")

        if not 0.0 <= self.initial_infected_share <= 1.0:
            raise ValueError("initial_infected_share must be between 0 and 1")

        if not 0.0 <= self.infection_probability <= 1.0:
            raise ValueError("infection_probability must be between 0 and 1")

        if not 0.0 <= self.recovery_probability <= 1.0:
            raise ValueError("recovery_probability must be between 0 and 1")

        if self.contact_radius <= 0:
            raise ValueError("contact_radius must be positive")

        self.world = GridWorld(
            width=self.width,
            height=self.height,
            torus=True,
            multi=False,
        )
        self.scheduler = StagedActivation(
            self,
            stages=["decide", "update_status"],
            shuffle=True,
        )
        self.new_infections = 0
        self.peak_infected = 0

        self._create_people()
        self.peak_infected = self.infected_count()
        self._register_recorders()

    def step(self) -> None:
        self.new_infections = 0
        self.scheduler.step()
        self.peak_infected = max(self.peak_infected, self.infected_count())

    def susceptible_count(self) -> int:
        return self._count_status("susceptible")

    def infected_count(self) -> int:
        return self._count_status("infected")

    def recovered_count(self) -> int:
        return self._count_status("recovered")

    def attack_rate(self) -> float:
        ever_infected = sum(int(getattr(agent, "ever_infected", False)) for agent in self.agents)
        return ever_infected / len(self.agents) if self.agents else 0.0

    def _count_status(self, status: str) -> int:
        return sum(int(getattr(agent, "status", None) == status) for agent in self.agents)

    def _create_people(self) -> None:
        initial_infected_count = round(self.n_agents * self.initial_infected_share)

        if self.initial_infected_share > 0.0:
            initial_infected_count = max(1, initial_infected_count)

        initial_infected_count = min(self.n_agents, initial_infected_count)
        initial_infected = set(
            int(index)
            for index in self.rng.choice(
                self.n_agents,
                size=initial_infected_count,
                replace=False,
            )
        )

        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        order = self.rng.permutation(len(positions))

        for person_id in range(self.n_agents):
            infected = person_id in initial_infected
            person = self.agents.create(
                Person,
                n=1,
                status="infected" if infected else "susceptible",
                ever_infected=infected,
                will_be_infected=False,
                will_recover=False,
            )[0]
            self.world.place(person, positions[int(order[person_id])])

    def _register_recorders(self) -> None:
        self.record.metric(
            "susceptible_count",
            lambda model: model.susceptible_count(),
        )
        self.record.metric(
            "infected_count",
            lambda model: model.infected_count(),
        )
        self.record.metric(
            "recovered_count",
            lambda model: model.recovered_count(),
        )
        self.record.metric(
            "new_infections",
            lambda model: model.new_infections,
        )
        self.record.metric(
            "peak_infected",
            lambda model: model.peak_infected,
        )
        self.record.metric(
            "attack_rate",
            lambda model: model.attack_rate(),
        )
        self.record.agent(
            "status",
            every=10,
            where=lambda agent: isinstance(agent, Person),
        )
        self.record.agent(
            "ever_infected",
            every=10,
            where=lambda agent: isinstance(agent, Person),
        )
