from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any, TypeVar

from abmforge.core.agent import Agent

if TYPE_CHECKING:
    from abmforge.core.model import Model

AgentT = TypeVar("AgentT", bound=Agent)


class AgentCollection:
    """Container and bulk-operation helper for model agents."""

    def __init__(self, model: Model) -> None:
        self.model = model
        self._agents: dict[int | str, Agent] = {}
        self._next_id = 1

    def __iter__(self) -> Iterator[Agent]:
        return iter(self._agents.values())

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, agent_or_id: object) -> bool:
        if isinstance(agent_or_id, Agent):
            return agent_or_id.unique_id in self._agents
        return agent_or_id in self._agents

    def _new_id(self) -> int:
        unique_id = self._next_id
        self._next_id += 1
        return unique_id

    def add(self, agent: Agent) -> Agent:
        """Add an existing agent to the collection."""
        if agent.unique_id in self._agents:
            raise ValueError(f"agent id already exists: {agent.unique_id!r}")
        self._agents[agent.unique_id] = agent
        return agent

    def create(self, agent_cls: type[AgentT], n: int = 1, **attrs: Any) -> list[AgentT]:
        """Create and add ``n`` agents of ``agent_cls``.

        The same keyword attributes are passed to every created agent.
        """
        if n < 0:
            raise ValueError("n must be non-negative")

        created: list[AgentT] = []
        for _ in range(n):
            agent = agent_cls(self.model, self._new_id(), **attrs)
            self.add(agent)
            created.append(agent)
        return created

    def remove(self, agent_or_id: Agent | int | str) -> Agent:
        """Remove and return an agent."""
        unique_id = agent_or_id.unique_id if isinstance(agent_or_id, Agent) else agent_or_id
        try:
            return self._agents.pop(unique_id)
        except KeyError as exc:
            raise KeyError(f"unknown agent id: {unique_id!r}") from exc

    def get(self, unique_id: int | str) -> Agent:
        """Return an agent by id."""
        try:
            return self._agents[unique_id]
        except KeyError as exc:
            raise KeyError(f"unknown agent id: {unique_id!r}") from exc

    def values(self) -> list[Agent]:
        """Return agents as a list."""
        return list(self._agents.values())

    def count(self) -> int:
        """Return the number of agents."""
        return len(self._agents)

    def do(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Call a method on every agent in insertion order."""
        for agent in list(self._agents.values()):
            getattr(agent, method_name)(*args, **kwargs)

    def shuffle_do(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Call a method on every agent in deterministic shuffled order."""
        agents = list(self._agents.values())
        if agents:
            order = self.model.rng.permutation(len(agents))
            agents = [agents[int(i)] for i in order]

        for agent in agents:
            getattr(agent, method_name)(*args, **kwargs)

    def select(self, predicate: Callable[[Agent], bool]) -> list[Agent]:
        """Return all agents matching a predicate."""
        return [agent for agent in self._agents.values() if predicate(agent)]

    def where(self, **attrs: Any) -> list[Agent]:
        """Return agents whose attributes match all provided values."""
        return [
            agent
            for agent in self._agents.values()
            if all(getattr(agent, key, None) == value for key, value in attrs.items())
        ]

    def count_where(self, **attrs: Any) -> int:
        """Count agents whose attributes match all provided values."""
        return len(self.where(**attrs))

    def by_type(self, agent_cls: type[AgentT]) -> list[AgentT]:
        """Return agents that are instances of ``agent_cls``."""
        return [agent for agent in self._agents.values() if isinstance(agent, agent_cls)]

    def attr(self, name: str) -> list[Any]:
        """Return an attribute from every agent that has it."""
        return [getattr(agent, name) for agent in self._agents.values() if hasattr(agent, name)]

    def sum(self, name: str) -> float:
        """Sum a numeric attribute across agents."""
        return float(sum(self.attr(name)))

    def mean(self, name: str) -> float:
        """Average a numeric attribute across agents."""
        values = self.attr(name)
        if not values:
            return float("nan")
        return float(sum(values) / len(values))

    def extend(self, agents: Iterable[Agent]) -> None:
        """Add multiple existing agents."""
        for agent in agents:
            self.add(agent)
