from __future__ import annotations

import json
from pathlib import Path

import abmforge

ROOT = Path(__file__).resolve().parents[1]


def test_citation_cff_exists_and_mentions_abmforge() -> None:
    path = ROOT / "CITATION.cff"

    assert path.exists()

    text = path.read_text(encoding="utf-8")

    assert "cff-version:" in text
    assert "ABMForge" in text
    assert abmforge.__version__ in text
    assert "Fatih" in text
    assert "Uludağ" in text
    assert "Apache-2.0" in text


def test_codemeta_json_exists_and_is_valid_json() -> None:
    path = ROOT / "codemeta.json"

    assert path.exists()

    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["@type"] == "SoftwareSourceCode"
    assert data["name"] == "ABMForge"
    assert data["version"] == abmforge.__version__
    assert data["license"] == "https://spdx.org/licenses/Apache-2.0"
    assert data["codeRepository"] == "https://github.com/fatihuludag-lab/abmforge"
