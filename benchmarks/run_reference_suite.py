from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    description: str
    commands: tuple[tuple[str, ...], ...]
    tags: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkResult:
    case: str
    repeat: int
    command_index: int
    command: tuple[str, ...]
    return_code: int
    duration_seconds: float


def cli_prefix() -> tuple[str, ...]:
    executable = shutil.which("abmforge")
    if executable:
        return (executable,)
    return (sys.executable, "-m", "abmforge.cli.main")


def benchmark_cases() -> tuple[BenchmarkCase, ...]:
    cli = cli_prefix()

    return (
        BenchmarkCase(
            name="cli_wealth_scenario_archive_smoke",
            description=(
                "Run the documented wealth scenario through the CLI, validate "
                "the archive, and produce a JSON summary."
            ),
            commands=(
                (
                    *cli,
                    "run",
                    "examples/scenarios/wealth_baseline.yaml",
                    "--archive",
                    "{archive}",
                    "--overwrite",
                ),
                (*cli, "validate", "{archive}"),
                (*cli, "summarize", "{archive}", "--json"),
            ),
            tags=("quick", "cli", "archive"),
        ),
    )


def environment_metadata() -> dict[str, str]:
    return {
        "python": sys.version.replace("\n", " "),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def format_command(command: Sequence[str], *, archive: Path, workdir: Path) -> list[str]:
    values = {
        "archive": str(archive),
        "workdir": str(workdir),
        "root": str(ROOT),
    }
    return [part.format(**values) for part in command]


def run_command(command: Sequence[str], *, cwd: Path) -> tuple[int, float]:
    start = time.perf_counter()
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    end = time.perf_counter()
    return completed.returncode, end - start


def run_case(case: BenchmarkCase, *, repeat: int, workdir: Path) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []

    for repeat_index in range(repeat):
        archive = workdir / f"{case.name}_{repeat_index}" / "archive"
        archive.parent.mkdir(parents=True, exist_ok=True)

        for command_index, command_template in enumerate(case.commands):
            command = format_command(command_template, archive=archive, workdir=workdir)
            return_code, duration = run_command(command, cwd=ROOT)
            results.append(
                BenchmarkResult(
                    case=case.name,
                    repeat=repeat_index,
                    command_index=command_index,
                    command=tuple(command),
                    return_code=return_code,
                    duration_seconds=duration,
                )
            )

            if return_code != 0:
                break

    return results


def write_results(
    *,
    output: Path,
    cases: Sequence[BenchmarkCase],
    results: Sequence[BenchmarkResult],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "benchmark-results-v0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "environment": environment_metadata(),
        "cases": [asdict(case) for case in cases],
        "results": [asdict(result) for result in results],
    }
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ABMForge reference benchmarks.")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List benchmark cases without running them.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run benchmark cases tagged as quick.",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat each selected case.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/benchmarks/reference_suite.json"),
        help="Path for JSON benchmark results.",
    )
    return parser


def select_cases(*, quick: bool) -> tuple[BenchmarkCase, ...]:
    cases = benchmark_cases()
    if quick:
        return tuple(case for case in cases if "quick" in case.tags)
    return cases


def main() -> int:
    args = build_parser().parse_args()
    cases = select_cases(quick=args.quick)

    if args.list:
        for case in cases:
            print(f"{case.name}: {case.description}")
        return 0

    if args.repeat < 1:
        print("--repeat must be at least 1", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="abmforge-benchmarks-") as temp_dir:
        workdir = Path(temp_dir)
        results: list[BenchmarkResult] = []
        for case in cases:
            results.extend(run_case(case, repeat=args.repeat, workdir=workdir))

    write_results(output=args.output, cases=cases, results=results)

    failed = [result for result in results if result.return_code != 0]
    if failed:
        print(f"Benchmark run completed with {len(failed)} failed command(s).")
        print(f"Results written to {args.output}")
        return 1

    print(f"Benchmark results written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
