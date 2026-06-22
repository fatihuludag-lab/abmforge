from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from itertools import product
from typing import Any


class ParameterGrid:
    """Cartesian product parameter grid for experiment runs.

    Parameter values are materialized during construction so one-shot iterables,
    such as generators, behave consistently across repeated calls to ``len()``
    and repeated iteration.
    """

    def __init__(self, parameters: Mapping[str, Iterable[Any]]) -> None:
        self.parameters: dict[str, tuple[Any, ...]] = {
            key: tuple(values) for key, values in parameters.items()
        }

    def __iter__(self) -> Iterator[dict[str, Any]]:
        keys = list(self.parameters.keys())
        values = [self.parameters[key] for key in keys]

        for combination in product(*values):
            yield dict(zip(keys, combination, strict=True))

    def __len__(self) -> int:
        total = 1
        for values in self.parameters.values():
            total *= len(values)
        return total
