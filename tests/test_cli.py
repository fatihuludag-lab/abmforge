from __future__ import annotations

import subprocess
import sys


def test_cli_version() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "abmforge.cli.main", "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == "0.1.0a1"
