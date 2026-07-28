from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_RELEASE_TAG_PATTERN = re.compile(
    r"^v"
    r"(0|[1-9][0-9]*)"
    r"\.(0|[1-9][0-9]*)"
    r"\.(0|[1-9][0-9]*)"
    r"(?:(?:a|b|rc)(0|[1-9][0-9]*))?"
    r"(?:\.post(0|[1-9][0-9]*))?"
    r"(?:\.dev(0|[1-9][0-9]*))?"
    r"$"
)


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
    return _extract(
        r'(?m)^__version__\s*:\s*str\s*=\s*"([^"]+)"\s*$',
        text,
        path,
    )


def validate_release_tag(tag: str) -> list[str]:
    errors: list[str] = []

    if not _RELEASE_TAG_PATTERN.fullmatch(tag):
        errors.append(
            "Release tag must use the form vMAJOR.MINOR.PATCH with an optional "
            "PEP 440 pre-release, post-release, or development suffix."
        )
        return errors

    tag_version = tag.removeprefix("v")
    pyproject_version = _read_pyproject_version()
    runtime_version = _read_runtime_version()

    if pyproject_version != runtime_version:
        errors.append(
            "Package version metadata is inconsistent: "
            f"pyproject.toml={pyproject_version}, runtime={runtime_version}"
        )

    if tag_version != pyproject_version:
        errors.append(
            f"Release tag version {tag_version!r} does not match "
            f"the package version {pyproject_version!r}."
        )

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an ABMForge release tag against package metadata."
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Git release tag, for example v0.3.0a1",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors = validate_release_tag(args.tag)

    if errors:
        print("Release tag check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Release tag check passed: {args.tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
