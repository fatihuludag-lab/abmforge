from __future__ import annotations

import subprocess
import sys


def test_wealth_example_runs() -> None:
    completed = subprocess.run(
        [sys.executable, "examples/wealth_model/run.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "status=completed" in completed.stdout
    assert "total_wealth" in completed.stdout
