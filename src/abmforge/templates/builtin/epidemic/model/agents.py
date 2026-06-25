from __future__ import annotations

from typing import TYPE_CHECKING, cast

from abmforge import Agent

if TYPE_CHECKING:
    from model.model import EpidemicTemplateModel


class Person(Agent):
    """Individual in a simple spatial SIR epidemic model."""

    def decide(self) -> None:
        model = cast("EpidemicTemplateModel", self.model)

        self.will_be_infected = False
        self.will_recover = False

        if self.status == "susceptible":
            infected_neighbors = sum(
                int(getattr(neighbor, "status", None) == "infected")
                for neighbor in self.neighbors(
                    radius=model.contact_radius,
                    include_center=False,
                )
            )

            if infected_neighbors <= 0:
                return

            infection_risk = 1.0 - ((1.0 - model.infection_probability) ** infected_neighbors)
            self.will_be_infected = self.rng.random() < infection_risk
            return

        if self.status == "infected":
            self.will_recover = self.rng.random() < model.recovery_probability

    def update_status(self) -> None:
        model = cast("EpidemicTemplateModel", self.model)

        if self.status == "susceptible" and self.will_be_infected:
            self.status = "infected"
            self.ever_infected = True
            model.new_infections += 1
            return

        if self.status == "infected" and self.will_recover:
            self.status = "recovered"
