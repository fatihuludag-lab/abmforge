"""Versioned execution fingerprints used for safe experiment recovery."""

from __future__ import annotations

import hashlib
import inspect
import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from abmforge.core.model import Model
from abmforge.repro.framework_provenance import FrameworkProvenanceV1
from abmforge.repro.input_provenance import (
    DECLARED_INPUT_IDENTITY_SCHEMA_VERSION,
    DeclaredInputIdentityV1,
)

EXECUTION_FINGERPRINT_V1_SCHEMA_VERSION = "execution-fingerprint-v1"
EXECUTION_FINGERPRINT_V2_SCHEMA_VERSION = "execution-fingerprint-v2"
EXECUTION_FINGERPRINT_V3_SCHEMA_VERSION = "execution-fingerprint-v3"

# Public alias for the schema emitted by current/default execution APIs.
EXECUTION_FINGERPRINT_SCHEMA_VERSION = EXECUTION_FINGERPRINT_V3_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class FrameworkExecutionIdentity:
    """Process-scoped framework identity used by execution fingerprints."""

    version: str
    package_tree_sha256: str | None

    @property
    def trusted(self) -> bool:
        return bool(self.version) and _is_sha256_hex(self.package_tree_sha256)


@lru_cache(maxsize=1)
def runtime_framework_execution_identity() -> FrameworkExecutionIdentity:
    """Return the cached runtime framework identity for this process."""

    provenance = FrameworkProvenanceV1.from_runtime()

    return FrameworkExecutionIdentity(
        version=provenance.version,
        package_tree_sha256=provenance.package_tree_sha256,
    )


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
    schema_version: str = EXECUTION_FINGERPRINT_V1_SCHEMA_VERSION

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
            self.schema_version == EXECUTION_FINGERPRINT_V1_SCHEMA_VERSION
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
        if data.get("schema_version") != EXECUTION_FINGERPRINT_V1_SCHEMA_VERSION:
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


def _is_sha256_hex(value: str | None) -> bool:
    if value is None or len(value) != 64:
        return False
    return all(character in "0123456789abcdef" for character in value)


def _valid_model_source_identity(
    source_kind: str,
    source_sha256: str | None,
) -> bool:
    if source_kind == _SOURCE_KIND_UNAVAILABLE:
        return source_sha256 is None

    if source_kind not in {
        "module-file-sha256",
        "class-source-sha256",
    }:
        return False

    return _is_sha256_hex(source_sha256)


@dataclass(frozen=True, slots=True)
class ExecutionFingerprintV2:
    """Framework-aware deterministic identity of one planned execution.

    Version 2 preserves the model and execution identity represented by V1 and
    additionally binds the fingerprint to the exact ABMForge runtime package
    tree used to plan and execute the run.
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
    framework_version: str
    framework_package_tree_sha256: str | None
    schema_version: str = EXECUTION_FINGERPRINT_V2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        model: type[Model],
        scenario: str,
        seed: int | None,
        steps: int | None,
        parameters: Mapping[str, Any],
        framework_version: str,
        framework_package_tree_sha256: str | None,
    ) -> ExecutionFingerprintV2:
        """Create a framework-aware fingerprint for one planned execution."""
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
            framework_version=framework_version,
            framework_package_tree_sha256=framework_package_tree_sha256,
        )

    @property
    def trusted(self) -> bool:
        """Whether this fingerprint is safe for automatic run reuse."""
        return (
            self.schema_version == EXECUTION_FINGERPRINT_V2_SCHEMA_VERSION
            and self.model_source_kind != _SOURCE_KIND_UNAVAILABLE
            and _valid_model_source_identity(
                self.model_source_kind,
                self.model_source_sha256,
            )
            and _is_sha256_hex(self.parameters_sha256)
            and bool(self.framework_version)
            and _is_sha256_hex(self.framework_package_tree_sha256)
        )

    @property
    def digest(self) -> str:
        """Return the canonical SHA-256 digest for the V2 payload."""
        return _sha256_json(self._payload())

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation including integrity data."""
        payload = self._payload()
        payload["digest"] = self.digest
        payload["trusted"] = self.trusted
        return payload

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> ExecutionFingerprintV2 | None:
        """Parse and integrity-check a serialized V2 fingerprint."""
        if data.get("schema_version") != EXECUTION_FINGERPRINT_V2_SCHEMA_VERSION:
            return None

        model_name = _required_string(data, "model_name")
        model_module = _required_string(data, "model_module")
        model_qualname = _required_string(data, "model_qualname")
        model_source_kind = _required_string(data, "model_source_kind")
        scenario = _required_string(data, "scenario")
        parameters_sha256 = _required_string(data, "parameters_sha256")
        framework_version = _required_string(data, "framework_version")

        if (
            model_name is None
            or model_module is None
            or model_qualname is None
            or model_source_kind is None
            or scenario is None
            or parameters_sha256 is None
            or framework_version is None
        ):
            return None

        source_value = data.get("model_source_sha256")
        if source_value is not None and not isinstance(source_value, str):
            return None

        if not _valid_model_source_identity(
            model_source_kind,
            source_value,
        ):
            return None

        if not _is_sha256_hex(parameters_sha256):
            return None

        framework_hash = data.get("framework_package_tree_sha256")
        if framework_hash is not None:
            if not isinstance(framework_hash, str):
                return None
            if not _is_sha256_hex(framework_hash):
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
            framework_version=framework_version,
            framework_package_tree_sha256=framework_hash,
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
            "framework_version": self.framework_version,
            "framework_package_tree_sha256": self.framework_package_tree_sha256,
        }


@dataclass(frozen=True, slots=True)
class ExecutionFingerprintV3:
    """Declared-input-aware deterministic identity for one execution."""

    model_name: str
    model_module: str
    model_qualname: str
    model_source_kind: str
    model_source_sha256: str | None
    scenario: str
    seed: int | None
    steps: int | None
    parameters_sha256: str
    framework_version: str
    framework_package_tree_sha256: str | None
    declared_input_schema_version: str
    input_artifact_count: int
    input_artifacts_sha256: str
    schema_version: str = EXECUTION_FINGERPRINT_V3_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        model: type[Model],
        scenario: str,
        seed: int | None,
        steps: int | None,
        parameters: Mapping[str, Any],
        framework_version: str,
        framework_package_tree_sha256: str | None,
        declared_inputs: DeclaredInputIdentityV1,
    ) -> ExecutionFingerprintV3:
        """Create an input-aware fingerprint for one planned execution."""
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
            framework_version=framework_version,
            framework_package_tree_sha256=framework_package_tree_sha256,
            declared_input_schema_version=declared_inputs.schema_version,
            input_artifact_count=declared_inputs.artifact_count,
            input_artifacts_sha256=declared_inputs.artifacts_sha256,
        )

    @property
    def trusted(self) -> bool:
        """Whether this V3 fingerprint is safe for automatic reuse."""
        return (
            self.schema_version == EXECUTION_FINGERPRINT_V3_SCHEMA_VERSION
            and self.model_source_kind != _SOURCE_KIND_UNAVAILABLE
            and _valid_model_source_identity(
                self.model_source_kind,
                self.model_source_sha256,
            )
            and _is_sha256_hex(self.parameters_sha256)
            and bool(self.framework_version)
            and _is_sha256_hex(self.framework_package_tree_sha256)
            and (self.declared_input_schema_version == DECLARED_INPUT_IDENTITY_SCHEMA_VERSION)
            and isinstance(self.input_artifact_count, int)
            and not isinstance(self.input_artifact_count, bool)
            and self.input_artifact_count >= 0
            and _is_sha256_hex(self.input_artifacts_sha256)
        )

    @property
    def digest(self) -> str:
        """Return the canonical SHA-256 digest for the V3 payload."""
        return _sha256_json(self._payload())

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation including integrity data."""
        payload = self._payload()
        payload["digest"] = self.digest
        payload["trusted"] = self.trusted
        return payload

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> ExecutionFingerprintV3 | None:
        """Parse and integrity-check a serialized V3 fingerprint."""
        if data.get("schema_version") != EXECUTION_FINGERPRINT_V3_SCHEMA_VERSION:
            return None

        model_name = _required_string(data, "model_name")
        model_module = _required_string(data, "model_module")
        model_qualname = _required_string(data, "model_qualname")
        model_source_kind = _required_string(data, "model_source_kind")
        scenario = _required_string(data, "scenario")
        parameters_sha256 = _required_string(data, "parameters_sha256")
        framework_version = _required_string(data, "framework_version")
        declared_input_schema_version = _required_string(
            data,
            "declared_input_schema_version",
        )
        input_artifacts_sha256 = _required_string(
            data,
            "input_artifacts_sha256",
        )

        if (
            model_name is None
            or model_module is None
            or model_qualname is None
            or model_source_kind is None
            or scenario is None
            or parameters_sha256 is None
            or framework_version is None
            or declared_input_schema_version is None
            or input_artifacts_sha256 is None
        ):
            return None

        source_value = data.get("model_source_sha256")
        if source_value is not None and not isinstance(source_value, str):
            return None

        if not _valid_model_source_identity(
            model_source_kind,
            source_value,
        ):
            return None

        if not _is_sha256_hex(parameters_sha256):
            return None

        framework_hash = data.get("framework_package_tree_sha256")
        if framework_hash is not None:
            if not isinstance(framework_hash, str):
                return None
            if not _is_sha256_hex(framework_hash):
                return None

        if declared_input_schema_version != DECLARED_INPUT_IDENTITY_SCHEMA_VERSION:
            return None

        input_artifact_count = data.get("input_artifact_count")
        if (
            not isinstance(input_artifact_count, int)
            or isinstance(input_artifact_count, bool)
            or input_artifact_count < 0
        ):
            return None

        if not _is_sha256_hex(input_artifacts_sha256):
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
            framework_version=framework_version,
            framework_package_tree_sha256=framework_hash,
            declared_input_schema_version=declared_input_schema_version,
            input_artifact_count=input_artifact_count,
            input_artifacts_sha256=input_artifacts_sha256,
        )

        digest = data.get("digest")
        if not isinstance(digest, str) or digest != fingerprint.digest:
            return None

        if not fingerprint.trusted:
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
            "framework_version": self.framework_version,
            "framework_package_tree_sha256": (self.framework_package_tree_sha256),
            "declared_input_schema_version": (self.declared_input_schema_version),
            "input_artifact_count": self.input_artifact_count,
            "input_artifacts_sha256": self.input_artifacts_sha256,
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
