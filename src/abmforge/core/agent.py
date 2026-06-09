from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from numpy.random import Generator

    from abmforge.core.model import Model


class Agent:
    """Base class for all agents.

    Subclasses usually override :meth:`step` and store their state as normal
    Python attributes.
    """

    def __init__(self, model: Model, unique_id: int | str, **attrs: Any) -> None:
        self.model = model
        self.unique_id = unique_id
        self.is_alive = True

        for key, value in attrs.items():
            setattr(self, key, value)

    @property
    def rng(self) -> Generator:
        """Return the model-level random number generator."""
        return self.model.rng

    def step(self) -> None:
        """Advance this agent by one model step.

        Override this method in user-defined agent classes.
        """

    def remove(self) -> None:
        """Remove this agent from its model."""
        self.model.remove_agent(self)

    def spawn(self, agent_cls: type[Agent], **attrs: Any) -> Agent:
        """Create a new agent of the given class in the same model."""
        return self.model.agents.create(agent_cls, n=1, **attrs)[0]

    def neighbors(self, **kwargs: Any) -> list[Agent]:
        """Return neighboring agents from the model's world/space."""
        if self.model.world is None:
            raise RuntimeError("This model has no world/space assigned.")

        if not hasattr(self.model.world, "neighbors"):
            raise RuntimeError("The current world does not implement neighbors().")

        return self.model.world.neighbors(self, **kwargs)
