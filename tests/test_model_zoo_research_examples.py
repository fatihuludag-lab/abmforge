from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXAMPLES = {
    "wealth_inequality": "wealth_analysis_summary.csv",
    "network_diffusion": "diffusion_analysis_summary.csv",
}


def _env(example_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    paths = [str(ROOT / "src"), str(example_dir)]
    existing = env.get("PYTHONPATH")
    if existing:
        paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    return env


def test_model_zoo_research_examples_have_required_files() -> None:
    for example in EXAMPLES:
        base = ROOT / "examples" / "model_zoo" / example

        for rel_path in [
            "README.md",
            "model.py",
            "configs/baseline.yaml",
            "configs/experiment.yaml",
            "analysis/analyze.py",
            "expected_outputs.md",
        ]:
            assert (base / rel_path).exists(), f"Missing {example}/{rel_path}"


def test_model_zoo_research_example_baselines_run_validate_and_analyze(
    tmp_path: Path,
) -> None:
    for example, expected_report in EXAMPLES.items():
        example_dir = ROOT / "examples" / "model_zoo" / example
        archive = tmp_path / example / "archive"
        env = _env(example_dir)

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
            cwd=example_dir,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        assert run_result.returncode == 0, run_result.stdout + run_result.stderr

        validate_result = subprocess.run(
            [sys.executable, "-m", "abmforge.cli.main", "validate", str(archive)],
            cwd=example_dir,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        assert validate_result.returncode == 0, validate_result.stdout + validate_result.stderr
        assert "Archive validation passed" in validate_result.stdout

        analysis_result = subprocess.run(
            [sys.executable, "analysis/analyze.py", str(archive)],
            cwd=example_dir,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        assert analysis_result.returncode == 0, analysis_result.stdout + analysis_result.stderr
        assert (archive / "reports" / expected_report).exists()


def test_model_zoo_research_docs_are_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Model Zoo Research Examples" in nav
    assert "model-zoo-research-examples.md" in nav
