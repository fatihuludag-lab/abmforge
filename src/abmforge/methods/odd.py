from __future__ import annotations

import inspect
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ODD_SCHEMA_VERSION = "abmforge.odd.v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_strings(values: Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    return [str(value) for value in values]


def _normalize_mapping(values: Mapping[str, Any] | None) -> dict[str, str]:
    if values is None:
        return {}
    return {str(key): str(value) for key, value in values.items()}


def _public_method_names(model_cls: type[Any]) -> list[str]:
    names: list[str] = []

    for name, _member in inspect.getmembers(model_cls, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        names.append(name)

    return sorted(set(names))


def _markdown_heading(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def _markdown_bullets(items: Iterable[str]) -> list[str]:
    return [f"- {item}" for item in items]


@dataclass(slots=True)
class ODDDocument:
    """ODD-style model documentation document.

    This class creates a lightweight, dependency-free ODD skeleton for ABMForge
    models. It does not claim that a model is fully documented or validated;
    instead, it provides a structured starting point that researchers can review,
    complete, and archive with their model outputs.
    """

    title: str
    purpose: str
    model_name: str
    model_module: str | None = None
    schema_version: str = ODD_SCHEMA_VERSION
    created_at: str = field(default_factory=_utc_now_iso)
    authors: list[str] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    scales: dict[str, str] = field(default_factory=dict)
    process_overview: list[str] = field(default_factory=list)
    design_concepts: dict[str, str] = field(default_factory=dict)
    initialization: list[str] = field(default_factory=list)
    input_data: list[dict[str, str]] = field(default_factory=list)
    submodels: list[dict[str, str]] = field(default_factory=list)
    decision_processes: list[dict[str, Any]] = field(default_factory=list)
    model_methods: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    manual_review_required: bool = True

    @classmethod
    def from_model(
        cls,
        model_cls: type[Any],
        *,
        purpose: str,
        title: str | None = None,
        authors: Iterable[str] | None = None,
        entities: Iterable[str] | None = None,
        scales: Mapping[str, Any] | None = None,
        process_overview: Iterable[str] | None = None,
        design_concepts: Mapping[str, Any] | None = None,
        initialization: Iterable[str] | None = None,
        input_data: Iterable[Mapping[str, Any]] | None = None,
        submodels: Iterable[Mapping[str, Any]] | None = None,
        decision_processes: Iterable[Mapping[str, Any]] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ODDDocument:
        """Create an ODD skeleton from a model class."""
        document = cls(
            title=title or f"ODD documentation for {model_cls.__name__}",
            purpose=purpose,
            model_name=model_cls.__name__,
            model_module=getattr(model_cls, "__module__", None),
            authors=_normalize_strings(authors),
            scales=_normalize_mapping(scales),
            process_overview=_normalize_strings(process_overview),
            design_concepts=_normalize_mapping(design_concepts),
            initialization=_normalize_strings(initialization),
            model_methods=_public_method_names(model_cls),
            metadata=dict(metadata or {}),
        )

        for entity in _normalize_strings(entities):
            document.add_entity(entity)

        for item in input_data or []:
            document.add_input_data(
                name=str(item.get("name", "")),
                description=str(item.get("description", "")),
                source=str(item.get("source", "")),
            )

        for item in submodels or []:
            document.add_submodel(
                name=str(item.get("name", "")),
                description=str(item.get("description", "")),
                source=str(item.get("source", "")),
            )

        for item in decision_processes or []:
            document.add_decision_process(
                name=str(item.get("name", "")),
                description=str(item.get("description", "")),
                actor=str(item.get("actor", "")),
                inputs=[str(value) for value in item.get("inputs", [])],
                outputs=[str(value) for value in item.get("outputs", [])],
                notes=str(item.get("notes", "")),
            )

        document.validate()
        return document

    def validate(self) -> None:
        """Validate minimum ODD document requirements."""
        if self.schema_version != ODD_SCHEMA_VERSION:
            raise ValueError(f"Unsupported ODD schema version: {self.schema_version}")

        if not self.title.strip():
            raise ValueError("ODD document title must not be empty")

        if not self.purpose.strip():
            raise ValueError("ODD document purpose must not be empty")

        if not self.model_name.strip():
            raise ValueError("ODD document model_name must not be empty")

    def completeness(self) -> dict[str, bool]:
        """Return a simple completeness checklist for major ODD sections."""
        return {
            "purpose": bool(self.purpose.strip()),
            "entities": bool(self.entities),
            "scales": bool(self.scales),
            "process_overview": bool(self.process_overview),
            "design_concepts": bool(self.design_concepts),
            "initialization": bool(self.initialization),
            "input_data": bool(self.input_data),
            "submodels": bool(self.submodels),
        }

    def add_author(self, name: str) -> ODDDocument:
        """Add an author name."""
        if name:
            self.authors.append(name)
        return self

    def add_entity(
        self,
        name: str,
        *,
        description: str = "",
        state_variables: Iterable[Mapping[str, Any]] | None = None,
    ) -> ODDDocument:
        """Add an entity type to the ODD document."""
        entity = {
            "name": name,
            "description": description,
            "state_variables": [
                {
                    "name": str(variable.get("name", "")),
                    "description": str(variable.get("description", "")),
                    "kind": str(variable.get("kind", "")),
                    "unit": str(variable.get("unit", "")),
                }
                for variable in state_variables or []
            ],
        }
        self.entities.append(entity)
        return self

    def add_state_variable(
        self,
        entity_name: str,
        name: str,
        *,
        description: str = "",
        kind: str = "",
        unit: str = "",
    ) -> ODDDocument:
        """Add a state variable to an existing or new entity."""
        entity = self._get_or_create_entity(entity_name)
        state_variables = entity.setdefault("state_variables", [])
        if not isinstance(state_variables, list):
            state_variables = []
            entity["state_variables"] = state_variables

        state_variables.append(
            {
                "name": name,
                "description": description,
                "kind": kind,
                "unit": unit,
            }
        )
        return self

    def add_scale(self, name: str, description: str) -> ODDDocument:
        """Add a temporal, spatial, social, or organizational scale."""
        self.scales[name] = description
        return self

    def add_process(self, description: str) -> ODDDocument:
        """Add a process overview item."""
        if description:
            self.process_overview.append(description)
        return self

    def add_design_concept(self, name: str, description: str) -> ODDDocument:
        """Add an ODD design concept."""
        self.design_concepts[name] = description
        return self

    def add_initialization(self, description: str) -> ODDDocument:
        """Add an initialization description."""
        if description:
            self.initialization.append(description)
        return self

    def add_input_data(
        self,
        *,
        name: str,
        description: str = "",
        source: str = "",
    ) -> ODDDocument:
        """Add an input data entry."""
        self.input_data.append(
            {
                "name": name,
                "description": description,
                "source": source,
            }
        )
        return self

    def add_submodel(
        self,
        *,
        name: str,
        description: str = "",
        source: str = "",
    ) -> ODDDocument:
        """Add a submodel entry."""
        self.submodels.append(
            {
                "name": name,
                "description": description,
                "source": source,
            }
        )
        return self

    def add_decision_process(
        self,
        *,
        name: str,
        description: str = "",
        actor: str = "",
        inputs: Iterable[str] | None = None,
        outputs: Iterable[str] | None = None,
        notes: str = "",
    ) -> ODDDocument:
        """Add an optional ODD+D-style decision process entry.

        This is intentionally lightweight. Full ODD+D support should be added as
        a later extension, but storing decision process metadata now helps users
        document human, institutional, or AI-agent decision rules.
        """
        self.decision_processes.append(
            {
                "name": name,
                "description": description,
                "actor": actor,
                "inputs": _normalize_strings(inputs),
                "outputs": _normalize_strings(outputs),
                "notes": notes,
            }
        )
        return self

    def to_dict(self) -> dict[str, Any]:
        """Return the ODD document as a JSON-serializable dictionary."""
        return {
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "title": self.title,
            "purpose": self.purpose,
            "model": {
                "name": self.model_name,
                "module": self.model_module,
                "public_methods": self.model_methods,
            },
            "authors": self.authors,
            "entities": self.entities,
            "scales": self.scales,
            "process_overview": self.process_overview,
            "design_concepts": self.design_concepts,
            "initialization": self.initialization,
            "input_data": self.input_data,
            "submodels": self.submodels,
            "decision_processes": self.decision_processes,
            "metadata": self.metadata,
            "manual_review_required": self.manual_review_required,
            "completeness": self.completeness(),
        }

    def to_json(self) -> str:
        """Return the ODD document as pretty-printed JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)

    def to_markdown(self) -> str:
        """Return the ODD document as Markdown."""
        lines: list[str] = []

        lines.append(_markdown_heading(1, self.title))
        lines.append("")
        lines.append("> Generated as an ABMForge ODD skeleton.")
        lines.append("> Manual review and completion are required before publication.")
        lines.append("")

        lines.append(_markdown_heading(2, "Metadata"))
        lines.append("")
        lines.append(f"- Schema version: `{self.schema_version}`")
        lines.append(f"- Created at: `{self.created_at}`")
        lines.append(f"- Model: `{self.model_name}`")
        if self.model_module:
            lines.append(f"- Module: `{self.model_module}`")
        if self.authors:
            lines.append(f"- Authors: {', '.join(self.authors)}")
        lines.append("")

        lines.append(_markdown_heading(2, "1. Purpose"))
        lines.append("")
        lines.append(self.purpose)
        lines.append("")

        lines.append(_markdown_heading(2, "2. Entities, State Variables, and Scales"))
        lines.append("")
        self._append_entities_markdown(lines)
        self._append_scales_markdown(lines)

        lines.append(_markdown_heading(2, "3. Process Overview and Scheduling"))
        lines.append("")
        if self.process_overview:
            lines.extend(_markdown_bullets(self.process_overview))
        else:
            lines.append("_To be completed._")
        lines.append("")

        lines.append(_markdown_heading(2, "4. Design Concepts"))
        lines.append("")
        if self.design_concepts:
            for name, description in self.design_concepts.items():
                lines.append(f"- **{name}:** {description}")
        else:
            lines.append("_To be completed._")
        lines.append("")

        lines.append(_markdown_heading(2, "5. Initialization"))
        lines.append("")
        if self.initialization:
            lines.extend(_markdown_bullets(self.initialization))
        else:
            lines.append("_To be completed._")
        lines.append("")

        lines.append(_markdown_heading(2, "6. Input Data"))
        lines.append("")
        self._append_input_data_markdown(lines)

        lines.append(_markdown_heading(2, "7. Submodels"))
        lines.append("")
        self._append_submodels_markdown(lines)

        lines.append(_markdown_heading(2, "8. Decision Processes"))
        lines.append("")
        self._append_decision_processes_markdown(lines)

        lines.append(_markdown_heading(2, "ABMForge Model Introspection"))
        lines.append("")
        if self.model_methods:
            lines.append("Public model methods detected:")
            lines.append("")
            lines.extend(_markdown_bullets(f"`{name}`" for name in self.model_methods))
        else:
            lines.append("_No public model methods detected._")
        lines.append("")

        lines.append(_markdown_heading(2, "Completeness Checklist"))
        lines.append("")
        for section, is_complete in self.completeness().items():
            mark = "x" if is_complete else " "
            lines.append(f"- [{mark}] {section}")
        lines.append("")

        lines.append(_markdown_heading(2, "Notes for Publication"))
        lines.append("")
        lines.append(
            "This document is an automatically generated skeleton. "
            "Authors should review every section, add missing methodological "
            "details, and align the final text with the model implementation, "
            "experiments, calibration, validation, and uncertainty analysis."
        )
        lines.append("")

        return "\n".join(lines)

    def write_markdown(self, path: str | Path) -> Path:
        """Write the ODD document to Markdown.

        If ``path`` is a directory or has no ``.md`` suffix, the document is
        written to ``path / "ODD.md"``.
        """
        output_path = Path(path)

        if output_path.suffix != ".md":
            output_path.mkdir(parents=True, exist_ok=True)
            output_path = output_path / "ODD.md"
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(self.to_markdown(), encoding="utf-8")
        return output_path

    def write_json(self, path: str | Path) -> Path:
        """Write the ODD document to JSON.

        If ``path`` is a directory or has no ``.json`` suffix, the document is
        written to ``path / "ODD.json"``.
        """
        output_path = Path(path)

        if output_path.suffix != ".json":
            output_path.mkdir(parents=True, exist_ok=True)
            output_path = output_path / "ODD.json"
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(self.to_json(), encoding="utf-8")
        return output_path

    def _get_or_create_entity(self, name: str) -> dict[str, Any]:
        for entity in self.entities:
            if entity.get("name") == name:
                return entity

        entity = {
            "name": name,
            "description": "",
            "state_variables": [],
        }
        self.entities.append(entity)
        return entity

    def _append_entities_markdown(self, lines: list[str]) -> None:
        if not self.entities:
            lines.append("_Entities and state variables to be completed._")
            lines.append("")
            return

        lines.append(_markdown_heading(3, "Entities and state variables"))
        lines.append("")

        for entity in self.entities:
            name = str(entity.get("name", ""))
            description = str(entity.get("description", ""))
            lines.append(f"- **{name}**")
            if description:
                lines.append(f"  - Description: {description}")

            state_variables = entity.get("state_variables", [])
            if isinstance(state_variables, list) and state_variables:
                lines.append("  - State variables:")
                for variable in state_variables:
                    if not isinstance(variable, Mapping):
                        continue
                    variable_name = str(variable.get("name", ""))
                    variable_description = str(variable.get("description", ""))
                    variable_kind = str(variable.get("kind", ""))
                    variable_unit = str(variable.get("unit", ""))
                    details = []
                    if variable_kind:
                        details.append(f"type: {variable_kind}")
                    if variable_unit:
                        details.append(f"unit: {variable_unit}")
                    suffix = f" ({', '.join(details)})" if details else ""
                    if variable_description:
                        lines.append(f"    - `{variable_name}`{suffix}: {variable_description}")
                    else:
                        lines.append(f"    - `{variable_name}`{suffix}")
        lines.append("")

    def _append_scales_markdown(self, lines: list[str]) -> None:
        lines.append(_markdown_heading(3, "Scales"))
        lines.append("")

        if self.scales:
            for name, description in self.scales.items():
                lines.append(f"- **{name}:** {description}")
        else:
            lines.append("_Scales to be completed._")
        lines.append("")

    def _append_input_data_markdown(self, lines: list[str]) -> None:
        if not self.input_data:
            lines.append("_No input data documented yet._")
            lines.append("")
            return

        for item in self.input_data:
            name = item.get("name", "")
            description = item.get("description", "")
            source = item.get("source", "")
            lines.append(f"- **{name}**")
            if description:
                lines.append(f"  - Description: {description}")
            if source:
                lines.append(f"  - Source: {source}")
        lines.append("")

    def _append_submodels_markdown(self, lines: list[str]) -> None:
        if not self.submodels:
            lines.append("_Submodels to be completed._")
            lines.append("")
            return

        for item in self.submodels:
            name = item.get("name", "")
            description = item.get("description", "")
            source = item.get("source", "")
            lines.append(f"- **{name}**")
            if description:
                lines.append(f"  - Description: {description}")
            if source:
                lines.append(f"  - Source: `{source}`")
        lines.append("")

    def _append_decision_processes_markdown(self, lines: list[str]) -> None:
        if not self.decision_processes:
            lines.append(
                "_No decision processes documented yet. "
                "For human, institutional, or AI-agent decision rules, add "
                "ODD+D-style decision process entries._"
            )
            lines.append("")
            return

        for item in self.decision_processes:
            name = item.get("name", "")
            description = item.get("description", "")
            actor = item.get("actor", "")
            inputs = item.get("inputs", [])
            outputs = item.get("outputs", [])
            notes = item.get("notes", "")

            lines.append(f"- **{name}**")
            if actor:
                lines.append(f"  - Actor: {actor}")
            if description:
                lines.append(f"  - Description: {description}")
            if inputs:
                lines.append(f"  - Inputs: {', '.join(str(value) for value in inputs)}")
            if outputs:
                lines.append(f"  - Outputs: {', '.join(str(value) for value in outputs)}")
            if notes:
                lines.append(f"  - Notes: {notes}")
        lines.append("")
