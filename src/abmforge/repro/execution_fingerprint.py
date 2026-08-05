"""Versioned execution fingerprints used for safe experiment recovery."""

from __future__ import annotations

import hashlib
import inspect
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from abmforge.core.model import Model

EXECUTION_FINGERPRINT_SCHEMA_VERSION = "execution-fingerprint-v1"

_SOURCE_KIND_MODULE_FILE = "module-file-sha256"
_SOURCE_KIND_CLASS_SOURCE = "class-source-sha256"
_SOURCE_KIND_UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ExecutionFingerprintV1:
    """Deterministic identity of a planned ABMForge execution.

    Version 1 covers the model source, model import identity, scenario name,
    seed, requested step count, and canonicalized model parameters.

    A fingerprint whose model source cannot be resolved is intentionally
    untrusted and must not be used to reuse an archived run.
    """

    model_name: str
    model_module: str
    model_qualname: str
    model_source_kind: str
    model_source_sha256: str | None
    scenario: str
    seed: int | None
    steps: int | None
    parameters_sha256: str
    schema_version: str = EXECUTION_FINGERPRINT_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        model: type[Model],
        scenario: str,
        seed: int | None,
        steps: int | None,
        parameters: Mapping[str, Any],
    ) -> ExecutionFingerprintV1:
        """Create a fingerprint for one planned execution."""
        source_kind, source_sha256 = _fingerprint_model_source(model)

        return cls(
            model_name=model.__name__,
            model_module=model.__module__,
            model_qualname=model.__qualname__,
            model_source_kind=source_kind,
            model_source_sha256=source_sha256,
            scenario=scenario,
            seed=seed,
            steps=steps,
            parameters_sha256=canonical_parameters_sha256(parameters),
        )

    @property
    def trusted(self) -> bool:
        """Whether this fingerprint is safe for automatic run reuse."""
        return (
            self.schema_version == EXECUTION_FINGERPRINT_SCHEMA_VERSION
            and self.model_source_kind != _SOURCE_KIND_UNAVAILABLE
            and self.model_source_sha256 is not None
        )

    @property
    def digest(self) -> str:
        """Return the canonical SHA-256 digest for the fingerprint payload."""
        return _sha256_json(self._payload())

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation including its digest."""
        payload = self._payload()
        payload["digest"] = self.digest
        payload["trusted"] = self.trusted
        return payload

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> ExecutionFingerprintV1 | None:
        """Parse and integrity-check a serialized fingerprint.

        Invalid, incomplete, unsupported, or tampered values return ``None``.
        Recovery code must treat ``None`` as an untrusted legacy identity.
        """
        if data.get("schema_version") != EXECUTION_FINGERPRINT_SCHEMA_VERSION:
            return None

        model_name = _required_string(data, "model_name")
        model_module = _required_string(data, "model_module")
        model_qualname = _required_string(data, "model_qualname")
        model_source_kind = _required_string(data, "model_source_kind")
        scenario = _required_string(data, "scenario")
        parameters_sha256 = _required_string(data, "parameters_sha256")

        if (
            model_name is None
            or model_module is None
            or model_qualname is None
            or model_source_kind is None
            or scenario is None
            or parameters_sha256 is None
        ):
            return None

        source_value = data.get("model_source_sha256")
        if source_value is not None and not isinstance(source_value, str):
            return None

        seed = _optional_integer(data.get("seed"))
        steps = _optional_integer(data.get("steps"))

        if data.get("seed") is not None and seed is None:
            return None
        if data.get("steps") is not None and steps is None:
            return None

        fingerprint = cls(
            model_name=model_name,
            model_module=model_module,
            model_qualname=model_qualname,
            model_source_kind=model_source_kind,
            model_source_sha256=source_value,
            scenario=scenario,
            seed=seed,
            steps=steps,
            parameters_sha256=parameters_sha256,
        )

        digest = data.get("digest")
        if not isinstance(digest, str) or digest != fingerprint.digest:
            return None

        return fingerprint

    def _payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "model_name": self.model_name,
            "model_module": self.model_module,
            "model_qualname": self.model_qualname,
            "model_source_kind": self.model_source_kind,
            "model_source_sha256": self.model_source_sha256,
            "scenario": self.scenario,
            "seed": self.seed,
            "steps": self.steps,
            "parameters_sha256": self.parameters_sha256,
        }


def canonical_parameters_sha256(parameters: Mapping[str, Any]) -> str:
    """Return the canonical SHA-256 digest for execution parameters."""
    return _sha256_json(parameters)


def _fingerprint_model_source(
    model: type[Model],
) -> tuple[str, str | None]:
    """Return the strongest locally available model-source fingerprint."""
    try:
        source_file = inspect.getsourcefile(model)
    except (OSError, TypeError):
        source_file = None

    if source_file is not None:
        path = Path(source_file)

        try:
            source_bytes = path.read_bytes()
        except OSError:
            pass
        else:
            return _SOURCE_KIND_MODULE_FILE, _sha256_bytes(source_bytes)

    try:
        source_text = inspect.getsource(model)
    except (OSError, TypeError):
        return _SOURCE_KIND_UNAVAILABLE, None

    return _SOURCE_KIND_CLASS_SOURCE, _sha256_bytes(source_text.encode("utf-8"))


def _sha256_json(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")

    return _sha256_bytes(encoded)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _required_string(
    data: Mapping[str, Any],
    key: str,
) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        return None
    return value


def _optional_integer(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value
