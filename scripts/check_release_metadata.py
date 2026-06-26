from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class MetadataValue:
    source: str
    value: str


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_pyproject_version() -> MetadataValue | None:
    text = read_text(ROOT / "pyproject.toml")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not match:
        return None
    return MetadataValue("pyproject.toml", match.group(1).strip())


def read_package_runtime_version() -> MetadataValue | None:
    """Read the source-tree package runtime version.

    ABMForge may expose ``abmforge.__version__`` through an imported version
    module rather than a literal assignment in ``__init__.py``. The release
    metadata checker should therefore validate the actual public runtime value.
    """

    src_path = str(ROOT / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    try:
        import abmforge
    except Exception as exc:
        raise RuntimeError("Could not import abmforge from the source tree") from exc

    version = getattr(abmforge, "__version__", None)
    if not version:
        return None

    return MetadataValue("src/abmforge runtime", str(version).strip())


def read_citation_version() -> MetadataValue | None:
    text = read_text(ROOT / "CITATION.cff")
    match = re.search(
        r"^version:\s*['\"]?([^'\"\n]+)['\"]?\s*$",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        return None
    return MetadataValue("CITATION.cff", match.group(1).strip())


def read_codemeta_version() -> MetadataValue | None:
    path = ROOT / "codemeta.json"
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("softwareVersion") or data.get("version")
    if not version:
        return None
    return MetadataValue("codemeta.json", str(version).strip())


def read_changelog_versions() -> list[str]:
    text = read_text(ROOT / "CHANGELOG.md")
    if not text:
        return []

    versions: list[str] = []
    patterns = [
        r"^##\s+\[?([0-9][^\]\s]*)\]?",
        r"^##\s+v([0-9][^\]\s]*)",
    ]
    for line in text.splitlines():
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                versions.append(match.group(1).strip())
                break
    return versions


def collect_version_values() -> list[MetadataValue]:
    values = [
        read_pyproject_version(),
        read_package_runtime_version(),
        read_citation_version(),
        read_codemeta_version(),
    ]
    return [value for value in values if value is not None]


def validate_metadata(*, strict: bool = False) -> list[str]:
    errors: list[str] = []
    values = collect_version_values()

    if not values:
        errors.append("No version metadata was found.")
        return errors

    unique_versions = {item.value for item in values}
    if len(unique_versions) > 1:
        errors.append("Conflicting version metadata values were found:")
        for item in values:
            errors.append(f"- {item.source}: {item.value}")

    required_sources = {
        "pyproject.toml",
        "src/abmforge runtime",
    }
    present_sources = {item.source for item in values}
    missing_required = sorted(required_sources - present_sources)
    for source in missing_required:
        errors.append(f"Missing required version metadata source: {source}")

    if strict:
        optional_sources = {
            "CITATION.cff",
            "codemeta.json",
        }
        missing_optional = sorted(optional_sources - present_sources)
        for source in missing_optional:
            errors.append(f"Missing formal-release metadata source: {source}")

        changelog_versions = read_changelog_versions()
        if not changelog_versions:
            errors.append("CHANGELOG.md has no release version headings.")
        else:
            declared_version = values[0].value
            normalized = {version.removeprefix("v") for version in changelog_versions}
            if declared_version.removeprefix("v") not in normalized:
                errors.append(
                    "CHANGELOG.md does not mention the current declared version: "
                    f"{declared_version}"
                )

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check ABMForge release metadata consistency.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require formal-release metadata such as citation and changelog entries.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    values = collect_version_values()
    print("Release metadata values:")
    for value in values:
        print(f"- {value.source}: {value.value}")

    changelog_versions = read_changelog_versions()
    if changelog_versions:
        print("Changelog versions:")
        for version in changelog_versions[:10]:
            print(f"- {version}")

    errors = validate_metadata(strict=args.strict)
    if errors:
        print("Release metadata check failed:")
        for error in errors:
            print(error)
        return 1

    print("Release metadata check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
