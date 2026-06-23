from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

DEFAULT_MAX_SEED = 2**32 - 1
SEED_SEQUENCE_VERSION = "seed-sequence-v1"


@dataclass(frozen=True, slots=True)
class SeedSequence:
    """Deterministic seed derivation helper for experiment workflows.

    The implementation uses a stable SHA-256 based derivation scheme instead of
    Python's built-in hash function. This keeps generated seeds deterministic
    across Python processes and platforms.
    """

    base_seed: int
    namespace: str = "abmforge.seed-sequence-v1"
    max_seed: int = DEFAULT_MAX_SEED

    def __post_init__(self) -> None:
        _validate_int("base_seed", self.base_seed, minimum=0)
        _validate_int("max_seed", self.max_seed, minimum=1)

        if not isinstance(self.namespace, str) or not self.namespace:
            raise ValueError("namespace must be a non-empty string")

    def derive(
        self,
        *,
        parameter_index: int = 0,
        replicate_index: int = 0,
        run_index: int | None = None,
        label: str | None = None,
    ) -> int:
        """Derive one deterministic seed.

        ``parameter_index`` and ``replicate_index`` are intended for experiment
        designs where each parameter combination may be repeated with multiple
        seeds. ``run_index`` is useful for linear run sequences.
        """
        parameter_index = _validate_int(
            "parameter_index",
            parameter_index,
            minimum=0,
        )
        replicate_index = _validate_int(
            "replicate_index",
            replicate_index,
            minimum=0,
        )

        if run_index is not None:
            run_index = _validate_int("run_index", run_index, minimum=0)

        if label is not None and not isinstance(label, str):
            raise TypeError("label must be a string or None")

        return self._derive_with_attempt(
            parameter_index=parameter_index,
            replicate_index=replicate_index,
            run_index=run_index,
            label=label,
            attempt=0,
        )

    def generate(
        self,
        count: int,
        *,
        start: int = 0,
        label: str | None = None,
    ) -> list[int]:
        """Generate a deterministic sequence of unique seeds."""
        count = _validate_int("count", count, minimum=0)
        start = _validate_int("start", start, minimum=0)

        if count > self.max_seed + 1:
            raise ValueError("count cannot exceed the number of available seeds")

        if label is not None and not isinstance(label, str):
            raise TypeError("label must be a string or None")

        seeds: list[int] = []
        used: set[int] = set()

        for offset in range(count):
            run_index = start + offset
            attempt = 0
            seed = self._derive_with_attempt(
                parameter_index=0,
                replicate_index=0,
                run_index=run_index,
                label=label,
                attempt=attempt,
            )

            while seed in used:
                attempt += 1
                seed = self._derive_with_attempt(
                    parameter_index=0,
                    replicate_index=0,
                    run_index=run_index,
                    label=label,
                    attempt=attempt,
                )

            seeds.append(seed)
            used.add(seed)

        return seeds

    def _derive_with_attempt(
        self,
        *,
        parameter_index: int,
        replicate_index: int,
        run_index: int | None,
        label: str | None,
        attempt: int,
    ) -> int:
        payload = {
            "attempt": attempt,
            "base_seed": self.base_seed,
            "label": label,
            "namespace": self.namespace,
            "parameter_index": parameter_index,
            "replicate_index": replicate_index,
            "run_index": run_index,
            "version": SEED_SEQUENCE_VERSION,
        }
        encoded = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        digest = hashlib.sha256(encoded).digest()
        return int.from_bytes(digest[:8], byteorder="big") % (self.max_seed + 1)


def _validate_int(name: str, value: int, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")

    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")

    return value
