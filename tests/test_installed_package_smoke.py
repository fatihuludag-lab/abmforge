from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def venv_executable(venv_dir: Path, name: str) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def run_command(command: list[str | Path], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [str(part) for part in command],
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, (
        f"command failed: {completed.args}\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )

    return completed


def build_wheel(tmp_path: Path) -> Path:
    dist_dir = tmp_path / "dist"

    run_command(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--outdir",
            dist_dir,
        ],
        cwd=ROOT,
    )

    wheels = sorted(dist_dir.glob("abmforge-*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def create_clean_venv(tmp_path: Path) -> Path:
    venv_dir = tmp_path / "installed-env"
    venv.EnvBuilder(with_pip=True).create(venv_dir)
    return venv_dir


def test_built_wheel_installs_and_imports_public_api(tmp_path: Path) -> None:
    wheel_path = build_wheel(tmp_path)
    venv_dir = create_clean_venv(tmp_path)
    python = venv_python(venv_dir)

    run_command([python, "-m", "pip", "install", "--upgrade", "pip"], cwd=tmp_path)
    run_command([python, "-m", "pip", "install", wheel_path], cwd=tmp_path)

    script = textwrap.dedent(
        """
        from importlib.metadata import version

        import abmforge
        from abmforge import (
            DATASET_SCHEMA_VERSION,
            Agent,
            Dataset,
            Model,
            Recorder,
            Scenario,
        )

        class TinyModel(Model):
            def setup(self):
                self.counter = 0

            def step(self):
                self.counter += 1

        result = Scenario(model=TinyModel, steps=2).run()

        assert abmforge.__version__ == version("abmforge")
        assert DATASET_SCHEMA_VERSION == "abmforge.dataset.v1"
        assert Agent is not None
        assert Dataset is not None
        assert Recorder is not None
        assert result.status == "completed"
        assert result.steps == 2
        assert result.model is not None
        assert result.model.counter == 2

        print(abmforge.__version__)
        """
    )

    completed = run_command([python, "-c", script], cwd=tmp_path)

    assert completed.stdout.strip()


def test_built_wheel_installs_console_script(tmp_path: Path) -> None:
    wheel_path = build_wheel(tmp_path)
    venv_dir = create_clean_venv(tmp_path)
    python = venv_python(venv_dir)
    abmforge = venv_executable(venv_dir, "abmforge")

    run_command([python, "-m", "pip", "install", "--upgrade", "pip"], cwd=tmp_path)
    run_command([python, "-m", "pip", "install", wheel_path], cwd=tmp_path)

    completed = run_command([abmforge, "--help"], cwd=tmp_path)

    output = f"{completed.stdout}\n{completed.stderr}".lower()
    assert "abmforge" in output
    assert "usage" in output
