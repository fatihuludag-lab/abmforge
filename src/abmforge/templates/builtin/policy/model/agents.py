from __future__ import annotations

from typing import TYPE_CHECKING, cast

from abmforge import Agent

if TYPE_CHECKING:
    from model.model import PolicyTemplateModel


class Resident(Agent):
    """Resident affected by a simple policy intervention."""

    def decide_compliance(self) -> None:
        model = cast("PolicyTemplateModel", self.model)

        if not self.offered_intervention:
            self.compliant = False
            return

        if self.compliant:
            return

        self.compliant = self.rng.random() < model.compliance_probability

    def update_outcome(self) -> None:
        model = cast("PolicyTemplateModel", self.model)

        neighbors = [
            neighbor
            for neighbor in self.neighbors(
                radius=model.neighborhood_radius,
                include_center=False,
            )
            if isinstance(neighbor, Resident)
        ]

        if neighbors:
            local_noncompliance = sum(
                int(not bool(getattr(neighbor, "compliant", False))) for neighbor in neighbors
            ) / len(neighbors)
        else:
            local_noncompliance = 0.0

        increment = (
            self.risk_score
            * model.outcome_pressure
            * (1.0 + model.spillover_weight * local_noncompliance)
        )

        if self.compliant:
            increment *= 1.0 - model.intervention_effect

        self.outcome_burden += increment
