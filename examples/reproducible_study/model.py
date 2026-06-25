from __future__ import annotations

from abmforge import Agent, Model


class Consumer(Agent):
    """Consumer agent in a small threshold-adoption model."""

    def step(self) -> None:
        if self.adopted:
            return

        peers = [agent for agent in self.model.agents if agent.unique_id != self.unique_id]
        if not peers:
            return

        sample_size = min(int(self.model.parameters.get("peer_sample_size", 5)), len(peers))
        chosen = self.model.rng.choice(len(peers), size=sample_size, replace=False)
        peer_adoption_share = sum(peers[int(index)].adopted for index in chosen) / sample_size

        peer_influence = float(self.model.parameters.get("peer_influence", 0.8))
        advertising = float(self.model.parameters.get("advertising", 0.05))
        adoption_signal = peer_influence * peer_adoption_share + advertising

        if adoption_signal >= self.threshold:
            self.adopted = True
            self.model.new_adoptions += 1


class ThresholdAdoptionModel(Model):
    """A compact research example for stochastic threshold adoption."""

    def setup(self) -> None:
        population = int(self.parameters.get("population", 40))
        initial_adoption_rate = float(self.parameters.get("initial_adoption_rate", 0.1))
        mean_threshold = float(self.parameters.get("adoption_threshold", 0.3))
        threshold_jitter = float(self.parameters.get("threshold_jitter", 0.04))

        self.new_adoptions = 0

        for _ in range(population):
            threshold = float(self.rng.normal(loc=mean_threshold, scale=threshold_jitter))
            threshold = max(0.0, min(1.0, threshold))
            adopted = bool(self.rng.random() < initial_adoption_rate)
            self.agents.create(
                Consumer,
                n=1,
                adopted=adopted,
                threshold=threshold,
            )

        self.record.metric("adopter_count", _adopter_count)
        self.record.metric("adoption_share", _adoption_share)
        self.record.metric("new_adoptions", lambda model: model.new_adoptions)
        self.record.metric("mean_threshold", _mean_threshold)
        self.record.agent("adopted", every=1)
        self.record.agent("threshold", every=4)

    def step(self) -> None:
        self.new_adoptions = 0
        self.agents.shuffle_do("step")


def _adopter_count(model: ThresholdAdoptionModel) -> int:
    return model.agents.count_where(adopted=True)


def _adoption_share(model: ThresholdAdoptionModel) -> float:
    population = model.agents.count()
    if population == 0:
        return 0.0
    return _adopter_count(model) / population


def _mean_threshold(model: ThresholdAdoptionModel) -> float:
    thresholds = [float(agent.threshold) for agent in model.agents]
    if not thresholds:
        return 0.0
    return sum(thresholds) / len(thresholds)
