from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_documentation_exists_and_is_conservative() -> None:
    docs = (ROOT / "docs" / "benchmarking.md").read_text(encoding="utf-8")

    assert "not a claim of superior performance" in docs
    assert "wall-clock" in docs
    assert "Recommended Local Protocol" in docs
    assert "Future Benchmark Areas" in docs
    assert "Mesa" in docs


def test_benchmark_runner_lists_reference_cases() -> None:
    script = ROOT / "benchmarks" / "run_reference_suite.py"

    result = subprocess.run(
        [sys.executable, str(script), "--list"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "cli_wealth_scenario_archive_smoke" in result.stdout


def test_benchmark_runner_exports_expected_metadata_functions() -> None:
    script = (ROOT / "benchmarks" / "run_reference_suite.py").read_text(encoding="utf-8")

    for term in [
        "benchmark-results-v0",
        "environment_metadata",
        "duration_seconds",
        "return_code",
        "--quick",
        "--repeat",
        "--output",
    ]:
        assert term in script


def test_benchmark_output_schema_is_json_serializable(tmp_path: Path) -> None:
    script = ROOT / "benchmarks" / "run_reference_suite.py"
    output = tmp_path / "benchmarks.json"

    result = subprocess.run(
        [sys.executable, str(script), "--list"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0

    sample = {
        "schema_version": "benchmark-results-v0",
        "created_at": "2026-01-01T00:00:00+00:00",
        "environment": {"python": "test"},
        "cases": [],
        "results": [],
    }
    output.write_text(json.dumps(sample), encoding="utf-8")

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "benchmark-results-v0"
    assert isinstance(loaded["results"], list)


def test_benchmarking_docs_are_listed_in_mkdocs_nav() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Benchmarking" in nav
    assert "benchmarking.md" in nav
