from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from itertools import product
from typing import Any


class ParameterGrid:
    """Cartesian product parameter grid for experiment runs."""

    def __init__(self, parameters: Mapping[str, Iterable[Any]]) -> None:
        self.parameters = dict(parameters)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        keys = list(self.parameters.keys())
        values = [list(self.parameters[key]) for key in keys]

        for combination in product(*values):
            yield dict(zip(keys, combination, strict=True))

    def __len__(self) -> int:
        total = 1
        for values in self.parameters.values():
            total *= len(list(values))
        return total
