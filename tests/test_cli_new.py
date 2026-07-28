from __future__ import annotations

from pathlib import Path

import pytest

import abmforge.cli.main as cli_main
import abmforge.templates.scaffold as scaffold_module
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


def test_cli_new_force_help_describes_safe_overwrite(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["new", "--help"])

    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    normalized_help = " ".join(captured.out.split())

    assert "preserve unrelated files" in normalized_help
    assert "template-managed files" in normalized_help


def test_cli_new_reports_filesystem_failure(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    def fail_create_project(*args, **kwargs):
        raise OSError("simulated filesystem failure")

    monkeypatch.setattr(cli_main, "create_project", fail_create_project)

    with pytest.raises(SystemExit) as exc_info:
        main(["new", str(tmp_path / "demo"), "--force"])

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Project creation failed:" in captured.err
    assert "simulated filesystem failure" in captured.err


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


def test_force_overwrites_template_files_and_preserves_unrelated_files(
    tmp_path,
) -> None:
    project = tmp_path / "demo"
    project.mkdir()

    notes = project / "research-notes.txt"
    notes.write_text("keep this work", encoding="utf-8")

    configs = project / "configs"
    configs.mkdir()
    baseline = configs / "baseline.yaml"
    baseline.write_text("outdated template content", encoding="utf-8")

    create_project(project, template="grid", force=True)

    assert notes.read_text(encoding="utf-8") == "keep this work"
    assert baseline.read_text(encoding="utf-8") != "outdated template content"


def test_force_replaces_file_that_conflicts_with_generated_outputs_directory(
    tmp_path,
) -> None:
    project = tmp_path / "demo"
    project.mkdir()

    notes = project / "research-notes.txt"
    notes.write_text("keep this work", encoding="utf-8")

    conflicting_outputs = project / "outputs"
    conflicting_outputs.write_text("not a directory", encoding="utf-8")

    create_project(project, template="grid", force=True)

    assert notes.read_text(encoding="utf-8") == "keep this work"
    assert conflicting_outputs.is_dir()
    assert (conflicting_outputs / ".gitkeep").is_file()


def test_force_replaces_file_that_conflicts_with_template_directory(
    tmp_path,
) -> None:
    project = tmp_path / "demo"
    project.mkdir()

    notes = project / "research-notes.txt"
    notes.write_text("keep this work", encoding="utf-8")

    conflicting_path = project / "configs"
    conflicting_path.write_text("not a directory", encoding="utf-8")

    create_project(project, template="grid", force=True)

    assert notes.read_text(encoding="utf-8") == "keep this work"
    assert conflicting_path.is_dir()
    assert (conflicting_path / "baseline.yaml").is_file()


def test_force_rejects_symbolic_links_and_preserves_existing_project(
    tmp_path,
    monkeypatch,
) -> None:
    project = tmp_path / "demo"
    project.mkdir()

    existing_file = project / "research-notes.txt"
    existing_file.write_text("keep this work", encoding="utf-8")

    link_entry = project / "external-data"
    link_entry.write_text("simulated link target", encoding="utf-8")

    original_is_symlink = Path.is_symlink

    def report_project_link(self):
        if self == link_entry:
            return True
        return original_is_symlink(self)

    monkeypatch.setattr(Path, "is_symlink", report_project_link)

    with pytest.raises(ProjectExistsError, match="symbolic link"):
        create_project(project, template="grid", force=True)

    assert project.is_dir()
    assert existing_file.read_text(encoding="utf-8") == "keep this work"
    assert link_entry.read_text(encoding="utf-8") == "simulated link target"
    assert not list(tmp_path.glob(".demo.abmforge-*"))


def test_force_restores_existing_project_when_final_swap_is_interrupted(
    tmp_path,
    monkeypatch,
) -> None:
    project = tmp_path / "demo"
    project.mkdir()

    existing_file = project / "research-notes.txt"
    existing_file.write_text("keep this work", encoding="utf-8")

    original_replace = Path.replace

    def interrupt_staging_install(self, target):
        destination = Path(target)

        if (
            self.name.startswith(f".{project.name}.abmforge-")
            and not self.name.endswith(".backup")
            and destination == project
        ):
            raise KeyboardInterrupt

        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", interrupt_staging_install)

    with pytest.raises(KeyboardInterrupt):
        create_project(project, template="grid", force=True)

    assert project.is_dir()
    assert existing_file.read_text(encoding="utf-8") == "keep this work"
    assert not list(tmp_path.glob(".demo.abmforge-*"))


def test_force_restores_existing_project_when_final_swap_fails(
    tmp_path,
    monkeypatch,
) -> None:
    project = tmp_path / "demo"
    project.mkdir()

    existing_file = project / "research-notes.txt"
    existing_file.write_text("keep this work", encoding="utf-8")

    original_replace = Path.replace

    def fail_staging_install(self, target):
        destination = Path(target)

        if (
            self.name.startswith(f".{project.name}.abmforge-")
            and not self.name.endswith(".backup")
            and destination == project
        ):
            raise OSError("simulated final swap failure")

        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", fail_staging_install)

    with pytest.raises(OSError, match="simulated final swap failure"):
        create_project(project, template="grid", force=True)

    assert project.is_dir()
    assert existing_file.read_text(encoding="utf-8") == "keep this work"
    assert not list(tmp_path.glob(".demo.abmforge-*"))


def test_force_preserves_existing_project_when_copy_fails(
    tmp_path,
    monkeypatch,
) -> None:
    project = tmp_path / "demo"
    project.mkdir()

    existing_file = project / "research-notes.txt"
    existing_file.write_text("keep this work", encoding="utf-8")

    def fail_copy(*args, **kwargs) -> None:
        raise OSError("simulated template copy failure")

    monkeypatch.setattr(scaffold_module, "_copy_tree", fail_copy)

    with pytest.raises(OSError, match="simulated template copy failure"):
        create_project(project, template="grid", force=True)

    assert project.is_dir()
    assert existing_file.read_text(encoding="utf-8") == "keep this work"


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
