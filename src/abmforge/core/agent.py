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
