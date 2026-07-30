from __future__ import annotations

import hashlib
import secrets
from collections.abc import Mapping
from contextlib import suppress
from datetime import datetime, timezone
from math import isfinite
from typing import Any
from uuid import uuid4

import numpy as np
from numpy.random import Generator

from abmforge.core.agent import Agent
from abmforge.core.agent_lifecycle import REMOVED
from abmforge.core.collection import AgentCollection
from abmforge.core.status import (
    COMPLETED,
    CREATED,
    FAILED,
    RUNNING,
    STOPPED,
    ModelStatus,
)
from abmforge.data.recorder import Recorder
from abmforge.randomness import RNG_STREAM_POLICY
from abmforge.time.queue import EventQueue

_RNG_STREAM_NAMESPACE = b"abmforge.named-rng-streams-v1"


def _derive_rng_stream_root(seed: int | None) -> str:
    """Return stable root material without consuming the default RNG."""
    if seed is None:
        return secrets.token_hex(32)

    normalized_seed = str(int(seed)).encode("ascii")

    return hashlib.sha256(_RNG_STREAM_NAMESPACE + b"\0seed\0" + normalized_seed).hexdigest()


_PROTECTED_MODEL_STATE_FIELDS = frozenset(
    {
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
        "scheduler",
        "schedule",
    }
)


_PROTECTED_AGENT_STATE_FIELDS = frozenset(
    {
        "model",
        "unique_id",
        "is_alive",
        "lifecycle_status",
        "world",
        "pos",
    }
)


class Model:
    """Base class for agent-based models."""

    def __init__(
        self, *, parameters: dict[str, Any] | None = None, seed: int | None = None
    ) -> None:
        self.parameters = dict(parameters or {})
        self.seed = seed
        self.rng: Generator = np.random.default_rng(seed)
        self._rng_stream_root = _derive_rng_stream_root(seed)
        self._rng_streams: dict[str, Generator] = {}

        self.run_id = f"run-{uuid4().hex}"
        self.created_at = datetime.now(timezone.utc).isoformat()

        self.steps = 0
        self.time = 0.0
        self.running = False
        self.stop_reason: str | None = None
        self.status: ModelStatus = CREATED

        self.agents = AgentCollection(model=self)
        self.events = EventQueue(model=self)
        self.record = Recorder(model=self)
        self.world: Any | None = None

    def rng_stream(self, name: str) -> Generator:
        """Return a cached deterministic random stream by component name.

        Named streams are derived independently from the model's default
        ``rng`` generator. Stream creation order and unrelated random draws
        therefore do not alter another named stream.
        """
        if not isinstance(name, str):
            raise TypeError("RNG stream name must be a string")

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("RNG stream name must be a non-empty string")

        existing = self._rng_streams.get(normalized_name)

        if existing is not None:
            return existing

        digest = hashlib.sha256()
        digest.update(_RNG_STREAM_NAMESPACE)
        digest.update(b"\0stream\0")
        digest.update(bytes.fromhex(self._rng_stream_root))
        digest.update(b"\0")
        digest.update(normalized_name.encode("utf-8"))

        derived_seed = int.from_bytes(
            digest.digest(),
            byteorder="big",
            signed=False,
        )
        generator = np.random.default_rng(derived_seed)

        self._rng_streams[normalized_name] = generator

        return generator

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
        self._run_for(steps, finalize=True)

    def _run_for(self, steps: int, *, finalize: bool) -> None:
        """Run model steps, optionally leaving the model active afterward."""
        if steps < 0:
            raise ValueError("steps must be non-negative")

        if self.status in {STOPPED, FAILED}:
            raise RuntimeError(f"Cannot run a {self.status} model")

        self.running = True
        self.status = RUNNING

        try:
            for _ in range(steps):
                if not self.running:
                    break

                self.events.process_due(time=self.time)
                self.step()

                self.steps += 1
                self.time += 1.0
                self.record.collect()
        except Exception:
            self.running = False
            self.status = FAILED
            raise

        if self.running and finalize:
            self.running = False
            self.status = COMPLETED

    def stop(self, reason: str = "stopped") -> None:
        """Stop the model run."""
        self.running = False
        self.stop_reason = reason
        self.status = STOPPED

    def remove_agent(
        self,
        agent_or_id: Any,
    ) -> Agent:
        """Remove an agent under the managed lifecycle contract."""
        unique_id = getattr(
            agent_or_id,
            "unique_id",
            agent_or_id,
        )

        if (
            hasattr(
                agent_or_id,
                "model",
            )
            and agent_or_id.model is not self
        ):
            raise ValueError("agent does not belong to this model")

        agent = self.agents.get(unique_id)

        if (
            hasattr(
                agent_or_id,
                "unique_id",
            )
            and agent is not agent_or_id
        ):
            raise ValueError("agent is not the current agent object for this model")

        agent_world = getattr(
            agent,
            "world",
            None,
        )

        if agent_world is not None:
            remove_from_world = getattr(
                agent_world,
                "remove",
                None,
            )

            if not callable(remove_from_world):
                raise TypeError("agent world does not implement remove()")

            # Spatial cleanup happens before lifecycle mutation. A space
            # failure therefore leaves collection membership, lifecycle
            # state, owned events, and records unchanged.
            remove_from_world(agent)

        elif self.world is not None and hasattr(
            self.world,
            "remove",
        ):
            # An attached model world may not contain every model agent.
            with suppress(KeyError):
                self.world.remove(agent)

        if hasattr(
            agent,
            "pos",
        ):
            delattr(
                agent,
                "pos",
            )

        if hasattr(
            agent,
            "world",
        ):
            delattr(
                agent,
                "world",
            )

        self.events.cancel_by_owner(unique_id)

        removed = self.agents._remove_direct(agent)

        agent.is_alive = False
        agent.lifecycle_status = REMOVED

        self.record.lifecycle(
            "agent_removed",
            agent_id=unique_id,
        )

        return removed

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        *,
        agent_classes: Mapping[str, type[Agent]] | None = None,
    ) -> Model:
        """Restore a basic model instance from Snapshot Schema v1.

        Restore API v1 intentionally supports only the base model state,
        parameters, step/time counters, run metadata, RNG state, and basic
        agent state. It does not yet restore world state, scheduler state,
        or event queue state.

        Custom agent classes are restored only when they are explicitly
        provided through ``agent_classes``. This avoids silently converting
        domain-specific agents into base ``Agent`` instances.
        """
        schema_version = snapshot.get("schema_version")
        if schema_version != "1.0":
            raise ValueError(f"Unsupported snapshot schema version: {schema_version}")

        parameters = snapshot.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValueError("Snapshot field 'parameters' must be a mapping")

        model = cls(parameters=parameters)

        rng_state = snapshot.get("rng_state")
        if rng_state is not None:
            if not isinstance(rng_state, dict):
                raise ValueError("Snapshot field 'rng_state' must be a mapping")
            model.rng.bit_generator.state = rng_state

        model._restore_rng_streams_from_snapshot(snapshot)

        run_id = snapshot.get("run_id")
        if not isinstance(run_id, str):
            raise ValueError("Snapshot field 'run_id' must be a string")
        model.run_id = run_id

        step = snapshot.get("step", 0)
        if isinstance(step, bool) or not isinstance(step, int) or step < 0:
            raise ValueError("Snapshot field 'step' must be a non-negative integer")
        model.steps = step

        time = snapshot.get("time", 0.0)
        if (
            isinstance(time, bool)
            or not isinstance(time, int | float)
            or not isfinite(float(time))
            or time < 0
        ):
            raise ValueError("Snapshot field 'time' must be a finite non-negative number")
        model.time = float(time)

        model_state = snapshot.get("model_state", {})
        if not isinstance(model_state, dict):
            raise ValueError("Snapshot field 'model_state' must be a mapping")

        for key, value in model_state.items():
            if not isinstance(key, str):
                raise ValueError("Snapshot model_state keys must be strings")
            if key.startswith("_"):
                raise ValueError(f"Snapshot model_state contains private model state field: {key}")
            if key in _PROTECTED_MODEL_STATE_FIELDS:
                raise ValueError(
                    f"Snapshot model_state contains protected model state field: {key}"
                )
            setattr(model, key, value)

        agent_class_registry: dict[str, type[Agent]] = {"Agent": Agent}
        if agent_classes is not None:
            agent_class_registry.update(agent_classes)

        agents = snapshot.get("agents", [])
        if not isinstance(agents, list):
            raise ValueError("Snapshot field 'agents' must be a list")

        for agent_snapshot in agents:
            if not isinstance(agent_snapshot, dict):
                raise ValueError("Each agent snapshot must be a mapping")

            legacy_agent_id = agent_snapshot.get("id")
            canonical_agent_id = agent_snapshot.get("agent_id")

            if (
                legacy_agent_id is not None
                and canonical_agent_id is not None
                and legacy_agent_id != canonical_agent_id
            ):
                raise ValueError("Snapshot agent identity fields 'id' and 'agent_id' do not match")

            agent_id = canonical_agent_id if canonical_agent_id is not None else legacy_agent_id
            if agent_id is None:
                raise ValueError("Agent snapshot must define 'agent_id' or 'id'")

            agent_type = agent_snapshot.get(
                "agent_type",
                agent_snapshot.get("type", "Agent"),
            )
            if not isinstance(agent_type, str):
                raise ValueError("Agent snapshot field 'agent_type' must be a string")

            try:
                agent_cls = agent_class_registry[agent_type]
            except KeyError as exc:
                raise ValueError(
                    f"Snapshot contains agent type {agent_type!r}, but no class was "
                    "provided. Pass it through the 'agent_classes' registry."
                ) from exc

            state = agent_snapshot.get("state", {})
            if not isinstance(state, dict):
                raise ValueError("Agent snapshot field 'state' must be a mapping")

            for key in state:
                if not isinstance(key, str):
                    raise ValueError("Snapshot agent state keys must be strings")
                if key.startswith("_"):
                    raise ValueError(
                        f"Snapshot agent state contains private agent state field: {key}"
                    )
                if key in _PROTECTED_AGENT_STATE_FIELDS:
                    raise ValueError(
                        f"Snapshot agent state contains protected agent state field: {key}"
                    )

            agent = agent_cls(model=model, unique_id=agent_id, **state)
            model.agents.add(agent)

        return model

    def _rng_snapshot_state(self) -> dict[str, Any]:
        """Return the legacy/default RNG state for Snapshot Schema v1."""
        return dict(self.rng.bit_generator.state)

    def _rng_stream_snapshot_states(
        self,
    ) -> dict[str, dict[str, Any]]:
        """Return opened named stream states in deterministic name order."""
        return {
            name: dict(self._rng_streams[name].bit_generator.state)
            for name in sorted(self._rng_streams)
        }

    def _restore_rng_streams_from_snapshot(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """Restore optional named-stream fields while accepting legacy snapshots."""
        field_names = (
            "rng_stream_policy",
            "rng_stream_root",
            "rng_streams",
        )
        present = [field_name in snapshot for field_name in field_names]

        if not any(present):
            return

        if not all(present):
            raise ValueError("Snapshot named RNG stream fields must be provided together")

        policy = snapshot["rng_stream_policy"]

        if policy != RNG_STREAM_POLICY:
            raise ValueError(f"Unsupported RNG stream policy: {policy!r}")

        root = snapshot["rng_stream_root"]

        if not isinstance(root, str) or len(root) != 64:
            raise ValueError("Snapshot field 'rng_stream_root' must be a 64-character hex string")

        try:
            bytes.fromhex(root)
        except ValueError as exc:
            raise ValueError(
                "Snapshot field 'rng_stream_root' must contain hexadecimal data"
            ) from exc

        stream_states = snapshot["rng_streams"]

        if not isinstance(
            stream_states,
            dict,
        ):
            raise ValueError("Snapshot field 'rng_streams' must be a mapping")

        validated_states: list[tuple[str, dict[str, Any]]] = []

        for name, state in stream_states.items():
            if not isinstance(name, str):
                raise ValueError("Snapshot RNG stream names must be strings")

            normalized_name = name.strip()

            if not normalized_name or normalized_name != name:
                raise ValueError("Snapshot RNG stream names must be normalized non-empty strings")

            if not isinstance(state, dict):
                raise ValueError(f"Snapshot RNG stream state for {name!r} must be a mapping")

            validated_states.append(
                (
                    normalized_name,
                    state,
                )
            )

        self._rng_stream_root = root
        self._rng_streams = {}

        for name, state in validated_states:
            generator = self.rng_stream(name)

            try:
                generator.bit_generator.state = state
            except (
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(f"Invalid RNG state for named stream {name!r}") from exc

    def _scheduler_metadata(self) -> dict[str, Any]:
        """Return JSON-serializable metadata for an attached scheduler.

        ABMForge models do not require a scheduler attribute, so this method
        treats scheduler metadata as optional audit data. It does not imply
        that scheduler instances are restored by ``from_snapshot``.
        """

        scheduler = None
        for attribute in ("_scheduler", "scheduler", "schedule"):
            candidate = getattr(self, attribute, None)
            if candidate is not None and hasattr(candidate, "step"):
                scheduler = candidate
                break

        if scheduler is None:
            return {
                "schema_version": "scheduler-metadata-v1",
                "attached": False,
            }

        to_metadata = getattr(scheduler, "to_metadata", None)
        if callable(to_metadata):
            metadata = dict(to_metadata())
        else:
            metadata = {
                "scheduler_type": type(scheduler).__name__,
                "module": type(scheduler).__module__,
            }

        metadata.setdefault("schema_version", "scheduler-metadata-v1")
        metadata.setdefault("attached", True)
        return metadata

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
            "rng_state": self._rng_snapshot_state(),
            "rng_stream_policy": RNG_STREAM_POLICY,
            "rng_stream_root": self._rng_stream_root,
            "rng_streams": self._rng_stream_snapshot_states(),
            "model_state": self._model_snapshot_state(),
            "agents": agents,
            "event_queue": self.events.snapshot_metadata(),
            "scheduler": self._scheduler_metadata(),
            "snapshot_id": f"snapshot-{uuid4().hex}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "parent_snapshot": None,
            "experiment_id": None,
            "manifest_hash": None,
        }

    def _model_snapshot_state(self) -> dict[str, Any]:
        """Return user-defined model state for Snapshot Schema v1."""
        return {
            key: value
            for key, value in vars(self).items()
            if key not in _PROTECTED_MODEL_STATE_FIELDS and not key.startswith("_")
        }

    @staticmethod
    def _agent_snapshot_state(agent: Any) -> dict[str, Any]:
        """Return user-defined agent state for Snapshot Schema v1."""
        return {
            key: value
            for key, value in vars(agent).items()
            if key not in _PROTECTED_AGENT_STATE_FIELDS and not key.startswith("_")
        }
