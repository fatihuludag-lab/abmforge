from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ProjectTemplate:
    """Description of a built-in ABMForge project template."""

    name: str
    description: str


class TemplateError(ValueError):
    """Raised when a requested project template is not available."""


class ProjectExistsError(FileExistsError):
    """Raised when a project path cannot be safely created."""


_TEMPLATE_DESCRIPTIONS = {
    "grid": "Minimal grid-based ABM study template for researcher workflows.",
    "epidemic": "Grid-based SIR epidemic ABM study template for researcher workflows.",
    "network": "Network-based diffusion ABM study template for researcher workflows.",
    "policy": "Policy intervention ABM study template for researcher workflows.",
    "resource": ("Renewable resource competition ABM study template for researcher workflows."),
    "segregation": (
        "Schelling-style spatial segregation ABM study template for researcher workflows."
    ),
    "research": ("End-to-end reproducible ABM research study template with analysis scaffold."),
}

_TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def list_templates() -> list[ProjectTemplate]:
    """Return built-in project templates available to the CLI."""

    return [
        ProjectTemplate(name=name, description=description)
        for name, description in sorted(_TEMPLATE_DESCRIPTIONS.items())
    ]


def template_names() -> tuple[str, ...]:
    """Return built-in project template names."""

    return tuple(template.name for template in list_templates())


def create_project(
    path: str | Path,
    *,
    template: str = "grid",
    force: bool = False,
) -> Path:
    """Create a new ABMForge study project from a built-in template.

    Parameters
    ----------
    path:
        Target project directory.
    template:
        Built-in template name.
    force:
        If true, replace an existing non-empty project only after the new
        project has been prepared successfully.

    Returns
    -------
    Path
        Absolute path to the created project directory.
    """

    available_templates = template_names()

    if template not in available_templates:
        available = ", ".join(available_templates)
        raise TemplateError(
            f"Unknown project template {template!r}. Available templates: {available}"
        )

    target = Path(path).expanduser().absolute()

    if target.is_symlink():
        raise ProjectExistsError(f"Project path must not be a symbolic link: {target}")

    if target.exists() and not target.is_dir():
        raise ProjectExistsError(f"Project path exists and is not a directory: {target}")

    if target.exists() and any(target.iterdir()) and not force:
        raise ProjectExistsError(
            "Project directory already exists and is not empty: "
            f"{target}. Use --force to overwrite it."
        )

    template_root = resources.files("abmforge.templates").joinpath("builtin").joinpath(template)

    if not template_root.is_dir():
        raise TemplateError(f"Template files are missing for {template!r}")

    target.parent.mkdir(parents=True, exist_ok=True)

    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{target.name}.abmforge-",
            dir=target.parent,
        )
    )

    context = {
        "project_name": target.name,
        "project_slug": _slugify_project_name(target.name),
    }

    try:
        if target.exists():
            _copy_existing_project_tree(target, staging)

        _copy_tree(template_root, staging, context)
        _finalize_project_tree(staging)
        _replace_project_tree(staging, target)
    except BaseException:
        _remove_path(staging, ignore_errors=True)
        raise

    return target


def _copy_existing_project_tree(source: Path, target: Path) -> None:
    for child in source.iterdir():
        if child.is_symlink():
            raise ProjectExistsError(
                "Existing project contains a symbolic link and cannot be "
                f"safely overwritten: {child}"
            )

        destination = target / child.name

        if child.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            _copy_existing_project_tree(child, destination)
            continue

        if child.is_file():
            shutil.copy2(child, destination)
            continue

        raise ProjectExistsError(
            f"Existing project contains an unsupported filesystem entry: {child}"
        )


def _finalize_project_tree(target: Path) -> None:
    outputs_dir = target / "outputs"

    if outputs_dir.is_symlink() or (outputs_dir.exists() and not outputs_dir.is_dir()):
        _remove_path(outputs_dir)

    outputs_dir.mkdir(exist_ok=True)
    (outputs_dir / ".gitkeep").write_text("", encoding="utf-8")

    model_init = target / "model" / "__init__.py"
    if model_init.parent.exists() and not model_init.exists():
        model_init.write_text(
            '"""Study model package generated by ABMForge."""\n',
            encoding="utf-8",
        )


def _replace_project_tree(staging: Path, target: Path) -> None:
    backup = staging.with_name(f"{staging.name}.backup")
    had_existing_target = target.exists()

    try:
        if had_existing_target:
            target.replace(backup)

        staging.replace(target)
    except BaseException:
        if had_existing_target and backup.exists():
            _remove_path(target, ignore_errors=True)
            backup.replace(target)
        raise
    else:
        _remove_path(backup, ignore_errors=True)


def _remove_path(path: Path, *, ignore_errors: bool = False) -> None:
    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.exists():
            shutil.rmtree(path)
    except OSError:
        if not ignore_errors:
            raise


def _copy_tree(source: Any, target: Path, context: dict[str, str]) -> None:
    for child in source.iterdir():
        if child.name == "__pycache__":
            continue

        destination = target / child.name

        if child.is_dir():
            if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
                _remove_path(destination)

            destination.mkdir(parents=True, exist_ok=True)
            _copy_tree(child, destination, context)
            continue

        _copy_file(child, destination, context)


def _copy_file(source: Any, destination: Path, context: dict[str, str]) -> None:
    if destination.is_symlink() or destination.exists():
        _remove_path(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)

    if _is_text_file(destination.name):
        text = source.read_text(encoding="utf-8")

        for key, value in context.items():
            text = text.replace(f"{{{{ {key} }}}}", value)
            text = text.replace(f"{{{{{key}}}}}", value)

        destination.write_text(text, encoding="utf-8")
        return

    destination.write_bytes(source.read_bytes())


def _is_text_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in _TEXT_SUFFIXES


def _slugify_project_name(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", name.strip().lower())
    slug = slug.strip("-._")
    return slug or "abmforge-study"
