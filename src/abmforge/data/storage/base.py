from __future__ import annotations

from typing import Any, Protocol


class StorageBackend(Protocol):
    """Protocol for ABMForge dataset storage backends."""

    run_id: str

    runs: list[dict[str, Any]]
    model_records: list[dict[str, Any]]
    agent_records: list[dict[str, Any]]
    event_records: list[dict[str, Any]]
    lifecycle_records: list[dict[str, Any]]
    errors: list[dict[str, Any]]

    def add_run(self, **metadata: Any) -> None: ...

    def update_last_run(self, **metadata: Any) -> None: ...

    def record_model(
        self,
        *,
        step: int,
        time: float,
        metric: str,
        value: Any,
    ) -> None: ...

    def record_agent(
        self,
        *,
        step: int,
        time: float,
        agent_id: int | str,
        agent_type: str,
        variable: str,
        value: Any,
    ) -> None: ...

    def record_event(
        self,
        *,
        step: int,
        time: float,
        event_id: int | str,
        owner: int | str | None,
        tags: list[str],
        status: str,
    ) -> None: ...

    def record_lifecycle(
        self,
        *,
        step: int,
        time: float,
        event: str,
        agent_id: int | str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None: ...

    def record_error(
        self,
        *,
        step: int,
        time: float,
        exception_type: str,
        message: str,
        component: str | None = None,
        traceback_text: str | None = None,
        recoverable: bool = False,
        event_id: int | str | None = None,
        agent_id: int | str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None: ...

    def validate(self) -> None: ...

    def schema_errors(self) -> list[str]: ...

    def to_dict(self) -> dict[str, Any]: ...
