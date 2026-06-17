from __future__ import annotations

from contextlib import suppress
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import numpy as np
from numpy.random import Generator

from abmforge.core.collection import AgentCollection
from abmforge.data.recorder import Recorder
from abmforge.time.queue import EventQueue


class Model:
    """Base class for agent-based models."""

    def __init__(
        self, *, parameters: dict[str, Any] | None = None, seed: int | None = None
    ) -> None:
        self.parameters = dict(parameters or {})
        self.seed = seed
        self.rng: Generator = np.random.default_rng(seed)

        self.run_id = f"run-{uuid4().hex}"
        self.created_at = datetime.now(timezone.utc).isoformat()

        self.steps = 0
        self.time = 0.0
        self.running = False
        self.stop_reason: str | None = None
        self.status = "created"

        self.agents = AgentCollection(model=self)
        self.events = EventQueue(model=self)
        self.record = Recorder(model=self)
        self.world: Any | None = None

    def setup(self) -> None:
        """Initialize model state before running.

        Override this method in user models.
        """

    def step(self) -> None:
        """Advance the model by one step.

        Override this method in user models.
        """

    def run_for(self, steps: int) -> None:
        """Run the model for a fixed number of steps."""
        if steps < 0:
            raise ValueError("steps must be non-negative")

        self.running = True
        self.status = "running"

        for _ in range(steps):
            if not self.running:
                break

            self.events.process_due(time=self.time)
            self.step()

            self.steps += 1
            self.time += 1.0
            self.record.collect()

        if self.running:
            self.status = "completed"

    def stop(self, reason: str = "stopped") -> None:
        """Stop the model run."""
        self.running = False
        self.stop_reason = reason
        self.status = "stopped"

    def remove_agent(self, agent_or_id: Any) -> None:
        """Remove an agent from the model, world, and owned event queue entries."""
        unique_id = getattr(agent_or_id, "unique_id", agent_or_id)
        agent = self.agents.get(unique_id)

        if agent is None:
            raise KeyError(f"Agent not found: {unique_id}")

        agent.is_alive = False
        self.events.cancel_by_owner(unique_id)

        if self.world is not None and hasattr(self.world, "remove"):
            with suppress(KeyError):
                self.world.remove(agent)

        self.agents.remove(unique_id)
        self.record.lifecycle("agent_removed", agent_id=unique_id)

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serializable model snapshot.

        Snapshot Schema v1 captures model metadata, user-defined model state,
        parameters, and agent state while preserving legacy snapshot fields.
        """
        agents = []

        for agent in self.agents:
            item: dict[str, Any] = {
                "id": agent.unique_id,
                "agent_id": agent.unique_id,
                "type": type(agent).__name__,
                "agent_type": type(agent).__name__,
                "state": self._agent_snapshot_state(agent),
            }

            if self.world is not None and hasattr(self.world, "position_of"):
                try:
                    position = self.world.position_of(agent)
                    item["position"] = list(position)
                except KeyError:
                    pass

            agents.append(item)

        return {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "step": self.steps,
            "time": self.time,
            "model": type(self).__name__,
            "model_name": type(self).__name__,
            "parameters": dict(self.parameters),
            "model_state": self._model_snapshot_state(),
            "agents": agents,
        }

    def _model_snapshot_state(self) -> dict[str, Any]:
        """Return user-defined model state for Snapshot Schema v1."""
        excluded = {
            "parameters",
            "seed",
            "rng",
            "run_id",
            "created_at",
            "steps",
            "time",
            "running",
            "stop_reason",
            "status",
            "agents",
            "events",
            "record",
            "world",
        }

        return {
            key: value
            for key, value in vars(self).items()
            if key not in excluded and not key.startswith("_")
        }

    @staticmethod
    def _agent_snapshot_state(agent: Any) -> dict[str, Any]:
        """Return user-defined agent state for Snapshot Schema v1."""
        excluded = {
            "model",
            "unique_id",
            "is_alive",
        }

        return {
            key: value
            for key, value in vars(agent).items()
            if key not in excluded and not key.startswith("_")
        }
