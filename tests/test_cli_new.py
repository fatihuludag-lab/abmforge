from __future__ import annotations

import pytest

from abmforge.cli.main import build_parser, main
from abmforge.templates import (
    ProjectExistsError,
    TemplateError,
    create_project,
    list_templates,
)


def test_build_parser_includes_new_command() -> None:
    help_text = build_parser().format_help()

    assert "new" in help_text


def test_list_templates_contains_grid() -> None:
    templates = list_templates()

    names = [template.name for template in templates]

    assert "grid" in names
    assert "network" in names
    assert all(template.description for template in templates)


def test_create_grid_project(tmp_path) -> None:
    project = create_project(tmp_path / "demo-study", template="grid")

    assert (project / "README.md").exists()
    assert (project / "pyproject.toml").exists()
    assert (project / "configs" / "baseline.yaml").exists()
    assert (project / "configs" / "experiment.yaml").exists()
    assert (project / "model" / "__init__.py").exists()
    assert (project / "model" / "agents.py").exists()
    assert (project / "model" / "model.py").exists()
    assert (project / "scripts" / "run_baseline.py").exists()
    assert (project / "tests" / "test_smoke.py").exists()
    assert (project / "outputs" / ".gitkeep").exists()

    readme = (project / "README.md").read_text(encoding="utf-8")
    assert "demo-study" in readme
    assert "{{" not in readme


def test_unknown_template_raises(tmp_path) -> None:
    with pytest.raises(TemplateError, match="Unknown project template"):
        create_project(tmp_path / "demo", template="does-not-exist")


def test_existing_non_empty_project_requires_force(tmp_path) -> None:
    project = tmp_path / "demo"
    project.mkdir()
    (project / "old.txt").write_text("old", encoding="utf-8")

    with pytest.raises(ProjectExistsError, match="not empty"):
        create_project(project, template="grid")


def test_force_recreates_project(tmp_path) -> None:
    project = tmp_path / "demo"
    project.mkdir()
    (project / "old.txt").write_text("old", encoding="utf-8")

    create_project(project, template="grid", force=True)

    assert not (project / "old.txt").exists()
    assert (project / "configs" / "baseline.yaml").exists()


def test_cli_new_creates_project(tmp_path, capsys) -> None:
    project = tmp_path / "demo-cli"

    main(["new", str(project), "--template", "grid"])

    captured = capsys.readouterr()
    assert "Created ABMForge project" in captured.out
    assert "Template: grid" in captured.out
    assert (project / "configs" / "baseline.yaml").exists()


def test_scaffolded_baseline_runs_from_project_root(tmp_path, monkeypatch) -> None:
    project = create_project(tmp_path / "demo-run", template="grid")

    monkeypatch.chdir(project)
    main(
        [
            "run",
            "configs/baseline.yaml",
            "--archive",
            "outputs/baseline",
            "--overwrite",
        ]
    )

    assert (project / "outputs" / "baseline" / "manifest.json").exists()
    assert (project / "outputs" / "baseline" / "reports" / "run_summary.json").exists()
