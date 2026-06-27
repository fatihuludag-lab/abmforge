from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from abmforge.templates import create_project, list_templates

ROOT = Path(__file__).resolve().parents[1]


def _subprocess_env(project: Path) -> dict[str, str]:
    env = os.environ.copy()
    paths = [str(ROOT / "src"), str(project)]
    existing = env.get("PYTHONPATH")
    if existing:
        paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    return env


def test_research_template_is_listed() -> None:
    templates = {template.name: template.description for template in list_templates()}

    assert "research" in templates
    assert "reproducible ABM research study" in templates["research"]


def test_research_template_creates_expected_project_files(tmp_path: Path) -> None:
    project = create_project(tmp_path / "my-study", template="research")

    expected_files = [
        "README.md",
        "configs/baseline.yaml",
        "configs/experiment.yaml",
        "model/__init__.py",
        "model/agents.py",
        "model/model.py",
        "analysis/analyze.py",
        "reports/README.md",
        "outputs/.gitkeep",
    ]

    for rel_path in expected_files:
        assert (project / rel_path).exists(), f"Missing generated file: {rel_path}"


def test_research_template_scenario_runs_and_validates_archive(tmp_path: Path) -> None:
    project = create_project(tmp_path / "my-study", template="research")
    archive = project / "outputs" / "baseline_archive"

    env = _subprocess_env(project)

    run_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "abmforge.cli.main",
            "run",
            "configs/baseline.yaml",
            "--archive",
            str(archive),
            "--overwrite",
        ],
        cwd=project,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert run_result.returncode == 0, run_result.stdout + run_result.stderr

    validate_result = subprocess.run(
        [sys.executable, "-m", "abmforge.cli.main", "validate", str(archive)],
        cwd=project,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert validate_result.returncode == 0, validate_result.stdout + validate_result.stderr
    assert "Archive validation passed" in validate_result.stdout


def test_research_template_analysis_script_runs(tmp_path: Path) -> None:
    project = create_project(tmp_path / "my-study", template="research")
    archive = project / "outputs" / "baseline_archive"

    env = _subprocess_env(project)

    run_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "abmforge.cli.main",
            "run",
            "configs/baseline.yaml",
            "--archive",
            str(archive),
            "--overwrite",
        ],
        cwd=project,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert run_result.returncode == 0, run_result.stdout + run_result.stderr

    analysis_result = subprocess.run(
        [sys.executable, "analysis/analyze.py", str(archive)],
        cwd=project,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert analysis_result.returncode == 0, analysis_result.stdout + analysis_result.stderr

    output = archive / "reports" / "analysis_summary.csv"
    assert output.exists()
    assert "latest_adoption_share" in output.read_text(encoding="utf-8")


def test_research_template_experiment_config_is_present_and_parseable(
    tmp_path: Path,
) -> None:
    project = create_project(tmp_path / "my-study", template="research")
    config = project / "configs" / "experiment.yaml"

    text = config.read_text(encoding="utf-8")

    assert "research-template-experiment" in text
    assert "peer_influence" in text
    assert "primary_metric: adoption_share" in text


def test_package_data_includes_research_template_analysis_scripts() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert '"templates/builtin/*/analysis/*.py"' in pyproject


def test_cli_templates_json_includes_research_template() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "abmforge.cli.main", "templates", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    payload = json.loads(result.stdout)
    names = [item["name"] for item in payload]

    assert "research" in names
