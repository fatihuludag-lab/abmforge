from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _extract(pattern: str, text: str, source: Path) -> str:
    match = re.search(pattern, text)
    if match is None:
        raise RuntimeError(f"Could not extract version from {source}")
    return match.group(1)


def _read_pyproject_version() -> str:
    path = ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    return _extract(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text, path)


def _read_fallback_version() -> str:
    path = ROOT / "src" / "abmforge" / "_version.py"
    text = path.read_text(encoding="utf-8")
    return _extract(r'(?m)^_FALLBACK_VERSION\s*=\s*"([^"]+)"\s*$', text, path)


def main() -> int:
    pyproject_version = _read_pyproject_version()
    fallback_version = _read_fallback_version()

    if pyproject_version != fallback_version:
        print(
            "Version mismatch:\n"
            f"  pyproject.toml: {pyproject_version}\n"
            f"  _version.py fallback: {fallback_version}",
            file=sys.stderr,
        )
        return 1

    print(f"Version consistency OK: {pyproject_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())