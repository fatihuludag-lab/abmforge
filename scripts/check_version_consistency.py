from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _extract(pattern: str, text: str, source: Path) -> str:
    match = re.search(pattern, text)
    if not match:
        raise RuntimeError(f"Could not extract version from {source}")
    return match.group(1)


def _read_pyproject_version() -> str:
    path = ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    return _extract(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text, path)


def _read_runtime_version() -> str:
    path = ROOT / "src" / "abmforge" / "_version.py"
    text = path.read_text(encoding="utf-8")

    patterns = [
        r'(?m)^__version__\s*:?\s*(?:str\s*=\s*)?"([^"]+)"\s*$',
        r'(?m)^_FALLBACK_VERSION\s*=\s*"([^"]+)"\s*$',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    raise RuntimeError(f"Could not extract version from {path}")


def main() -> int:
    pyproject_version = _read_pyproject_version()
    runtime_version = _read_runtime_version()

    print(f"pyproject.toml version: {pyproject_version}")
    print(f"runtime version: {runtime_version}")

    if pyproject_version != runtime_version:
        print("Version mismatch detected.")
        return 1

    print("Version consistency check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
