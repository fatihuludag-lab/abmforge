from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.3.0a1"


def normalized_text(text: str) -> str:
    return " ".join(text.split())


def test_project_version_metadata_is_consistent() -> None:
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    codemeta = json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))

    pyproject_version_match = re.search(
        r'(?m)^version\s*=\s*["\']([^"\']+)["\']',
        pyproject_text,
    )

    version_text = (ROOT / "src" / "abmforge" / "_version.py").read_text(encoding="utf-8")
    package_version_match = re.search(
        r'(?m)^(?:__version__|VERSION)(?:\s*:\s*str)?\s*=\s*["\']([^"\']+)["\']',
        version_text,
    )

    assert pyproject_version_match is not None
    assert package_version_match is not None
    assert pyproject_version_match.group(1) == EXPECTED_VERSION
    assert package_version_match.group(1) == EXPECTED_VERSION
    assert citation["version"] == EXPECTED_VERSION
    assert codemeta["version"] == EXPECTED_VERSION


def test_license_contains_canonical_apache_2_0_sections() -> None:
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    compact_license_text = normalized_text(license_text)

    assert "Apache License" in license_text
    assert "Version 2.0, January 2004" in license_text
    assert "APPENDIX: How to apply the Apache License to your work." in license_text
    assert (
        "patent licenses granted to You under this License for that Work shall terminate"
        in compact_license_text
    )
    assert "limitations under the License" in compact_license_text


def test_release_documentation_contains_current_development_state() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")

    assert "## Unreleased" in changelog
    assert f"Current development version: `{EXPECTED_VERSION}`." in changelog
    assert f"Current development version: `{EXPECTED_VERSION}`." in release_notes
    assert "not a stable release" in release_notes.lower()
