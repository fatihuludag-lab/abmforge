from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

PositionT = TypeVar("PositionT")


def agent_id(agent_or_id: Any) -> Any:
    """Return the identifier represented by an agent object or raw id."""
    return getattr(
        agent_or_id,
        "unique_id",
        agent_or_id,
    )


def ensure_new_placement(
    agent: Any,
    *,
    space: Any,
    positions: Mapping[Any, Any],
    agents: Mapping[Any, Any],
) -> None:
    """Validate that an agent can be newly indexed by a space."""
    unique_id = agent.unique_id

    if unique_id in positions:
        stored = agents.get(unique_id)

        if stored is not agent:
            raise ValueError(f"different agent object is already placed for id: {unique_id!r}")

        raise ValueError(f"agent is already placed: {unique_id!r}")

    current_world = getattr(
        agent,
        "world",
        None,
    )

    if current_world is not None and current_world is not space:
        raise ValueError(f"agent is already placed in another space: {unique_id!r}")

    if current_world is space:
        raise ValueError(f"agent references this space without an indexed position: {unique_id!r}")


def resolve_placed_agent(
    agent_or_id: Any,
    *,
    positions: Mapping[Any, PositionT],
    agents: Mapping[Any, Any],
) -> tuple[Any, Any, PositionT]:
    """Return a validated placed-agent identity and position."""
    unique_id = agent_id(agent_or_id)

    try:
        position = positions[unique_id]
    except KeyError as exc:
        raise KeyError(f"agent is not placed: {unique_id!r}") from exc

    try:
        stored = agents[unique_id]
    except KeyError as exc:
        raise RuntimeError(
            f"space identity index is inconsistent for agent id: {unique_id!r}"
        ) from exc

    if (
        hasattr(
            agent_or_id,
            "unique_id",
        )
        and stored is not agent_or_id
    ):
        raise ValueError(f"different agent object is placed for id: {unique_id!r}")

    return (
        unique_id,
        stored,
        position,
    )


def clear_spatial_attributes(
    agent: Any,
    *,
    space: Any,
) -> None:
    """Clear framework-managed spatial references after removal."""
    if hasattr(
        agent,
        "pos",
    ):
        delattr(
            agent,
            "pos",
        )

    if (
        getattr(
            agent,
            "world",
            None,
        )
        is space
    ):
        delattr(
            agent,
            "world",
        )
