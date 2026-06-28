from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _paper_body(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def test_software_paper_package_exists() -> None:
    assert (ROOT / "paper.md").is_file()
    assert (ROOT / "paper.bib").is_file()
    assert (ROOT / "docs" / "software-paper-package.md").is_file()


def test_paper_has_required_joss_style_sections() -> None:
    paper = (ROOT / "paper.md").read_text(encoding="utf-8")

    required_terms = [
        "title:",
        "authors:",
        "affiliations:",
        "bibliography: paper.bib",
        "# Summary",
        "# Statement of need",
        "# Design and functionality",
        "# Reproducibility workflow",
        "# Example use case",
        "# Limitations and future work",
    ]

    for term in required_terms:
        assert term in paper


def test_paper_word_count_is_joss_sized() -> None:
    body = _paper_body((ROOT / "paper.md").read_text(encoding="utf-8"))
    words = re.findall(r"\b[\w-]+\b", body)

    assert 750 <= len(words) <= 1750


def test_paper_bibliography_covers_reference_tools_and_odd() -> None:
    bib = (ROOT / "paper.bib").read_text(encoding="utf-8").lower()

    for key in ["mesa", "netlogo", "repast", "mason", "agentsjl", "odd"]:
        assert f"{{{key}," in bib
