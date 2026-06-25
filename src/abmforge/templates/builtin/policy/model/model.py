from __future__ import annotations

from statistics import fmean

from model.agents import Resident

from abmforge import GridWorld, Model
from abmforge.scheduling import StagedActivation


class PolicyTemplateModel(Model):
    """Minimal policy-intervention model for researcher scaffolds."""

    def setup(self) -> None:
        self.width = int(self.parameters.get("width", 25))
        self.height = int(self.parameters.get("height", 25))
        self.n_agents = int(self.parameters.get("n_agents", 300))
        self.high_risk_share = float(self.parameters.get("high_risk_share", 0.30))
        self.intervention_coverage = float(self.parameters.get("intervention_coverage", 0.40))
        self.intervention_capacity = int(
            self.parameters.get("intervention_capacity", self.n_agents)
        )
        self.targeting_rule = str(self.parameters.get("targeting_rule", "risk_priority"))
        self.compliance_probability = float(self.parameters.get("compliance_probability", 0.75))
        self.intervention_effect = float(self.parameters.get("intervention_effect", 0.55))
        self.outcome_pressure = float(self.parameters.get("outcome_pressure", 1.0))
        self.neighborhood_radius = int(self.parameters.get("neighborhood_radius", 1))
        self.spillover_weight = float(self.parameters.get("spillover_weight", 0.10))

        self._validate_parameters()

        self.world = GridWorld(
            width=self.width,
            height=self.height,
            torus=True,
            multi=False,
        )
        self.scheduler = StagedActivation(
            self,
            stages=["decide_compliance", "update_outcome"],
            shuffle=True,
        )

        self._create_residents()
        self._assign_intervention()
        self._register_recorders()

    def step(self) -> None:
        self.scheduler.step()

    def treated_agents(self) -> int:
        return sum(
            int(bool(getattr(agent, "offered_intervention", False))) for agent in self.agents
        )

    def compliant_agents(self) -> int:
        return sum(int(bool(getattr(agent, "compliant", False))) for agent in self.agents)

    def untreated_high_risk_agents(self) -> int:
        return sum(
            int(
                bool(getattr(agent, "high_risk", False))
                and not bool(getattr(agent, "offered_intervention", False))
            )
            for agent in self.agents
        )

    def outcome_burden(self) -> float:
        return sum(float(getattr(agent, "outcome_burden", 0.0)) for agent in self.agents)

    def mean_outcome_burden(self) -> float:
        return self.outcome_burden() / len(self.agents) if self.agents else 0.0

    def coverage_rate(self) -> float:
        return self.treated_agents() / len(self.agents) if self.agents else 0.0

    def compliance_rate(self) -> float:
        treated = self.treated_agents()
        return self.compliant_agents() / treated if treated else 0.0

    def equity_gap(self) -> float:
        return self._mean_burden(high_risk=True) - self._mean_burden(high_risk=False)

    def _mean_burden(self, *, high_risk: bool) -> float:
        values = [
            float(getattr(agent, "outcome_burden", 0.0))
            for agent in self.agents
            if bool(getattr(agent, "high_risk", False)) == high_risk
        ]
        return fmean(values) if values else 0.0

    def _validate_parameters(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")

        if self.n_agents <= 0:
            raise ValueError("n_agents must be positive")

        if self.n_agents > self.width * self.height:
            raise ValueError("n_agents cannot exceed the number of grid cells when multi=False")

        if not 0.0 <= self.high_risk_share <= 1.0:
            raise ValueError("high_risk_share must be between 0 and 1")

        if not 0.0 <= self.intervention_coverage <= 1.0:
            raise ValueError("intervention_coverage must be between 0 and 1")

        if self.intervention_capacity < 0:
            raise ValueError("intervention_capacity must be non-negative")

        if self.targeting_rule not in {"random", "risk_priority"}:
            raise ValueError("targeting_rule must be 'random' or 'risk_priority'")

        if not 0.0 <= self.compliance_probability <= 1.0:
            raise ValueError("compliance_probability must be between 0 and 1")

        if not 0.0 <= self.intervention_effect <= 1.0:
            raise ValueError("intervention_effect must be between 0 and 1")

        if self.outcome_pressure < 0.0:
            raise ValueError("outcome_pressure must be non-negative")

        if self.neighborhood_radius <= 0:
            raise ValueError("neighborhood_radius must be positive")

        if self.spillover_weight < 0.0:
            raise ValueError("spillover_weight must be non-negative")

    def _create_residents(self) -> None:
        high_risk_count = round(self.n_agents * self.high_risk_share)
        high_risk_ids = set(
            int(index)
            for index in self.rng.choice(
                self.n_agents,
                size=high_risk_count,
                replace=False,
            )
        )
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        order = self.rng.permutation(len(positions))

        for resident_id in range(self.n_agents):
            high_risk = resident_id in high_risk_ids
            risk_score = float(self.rng.normal(1.6 if high_risk else 0.8, 0.15))
            risk_score = max(0.1, risk_score)

            resident = self.agents.create(
                Resident,
                n=1,
                high_risk=high_risk,
                risk_score=risk_score,
                offered_intervention=False,
                compliant=False,
                outcome_burden=0.0,
            )[0]
            self.world.place(resident, positions[int(order[resident_id])])

    def _assign_intervention(self) -> None:
        requested = round(self.n_agents * self.intervention_coverage)
        intervention_count = min(requested, self.intervention_capacity, self.n_agents)

        agents = list(self.agents)

        if self.targeting_rule == "random":
            order = [agents[int(index)] for index in self.rng.permutation(len(agents))]
        else:
            tie_breakers = {agent.unique_id: float(self.rng.random()) for agent in agents}
            order = sorted(
                agents,
                key=lambda agent: (
                    -float(getattr(agent, "risk_score", 0.0)),
                    tie_breakers[agent.unique_id],
                ),
            )

        for agent in order[:intervention_count]:
            agent.offered_intervention = True

    def _register_recorders(self) -> None:
        self.record.metric(
            "outcome_burden",
            lambda model: model.outcome_burden(),
        )
        self.record.metric(
            "mean_outcome_burden",
            lambda model: model.mean_outcome_burden(),
        )
        self.record.metric(
            "treated_agents",
            lambda model: model.treated_agents(),
        )
        self.record.metric(
            "coverage_rate",
            lambda model: model.coverage_rate(),
        )
        self.record.metric(
            "compliance_rate",
            lambda model: model.compliance_rate(),
        )
        self.record.metric(
            "untreated_high_risk_agents",
            lambda model: model.untreated_high_risk_agents(),
        )
        self.record.metric(
            "equity_gap",
            lambda model: model.equity_gap(),
        )
        self.record.agent(
            "high_risk",
            when=lambda model: model.steps == 1,
            where=lambda agent: isinstance(agent, Resident),
        )
        self.record.agent(
            "offered_intervention",
            when=lambda model: model.steps == 1,
            where=lambda agent: isinstance(agent, Resident),
        )
        self.record.agent(
            "compliant",
            every=10,
            where=lambda agent: isinstance(agent, Resident),
        )
        self.record.agent(
            "outcome_burden",
            every=10,
            where=lambda agent: isinstance(agent, Resident),
        )
