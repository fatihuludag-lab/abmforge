from __future__ import annotations

import abmforge
from abmforge.cli.main import format_citation, main


def test_format_citation_text_contains_version_and_repository() -> None:
    citation = format_citation("text")

    assert "ABMForge" in citation
    assert abmforge.__version__ in citation
    assert "https://github.com/fatihuludag-lab/abmforge" in citation
    assert "CITATION.cff" in citation


def test_format_citation_bibtex_contains_software_entry() -> None:
    citation = format_citation("bibtex")

    assert citation.startswith("@software{uludag_abmforge_2026")
    assert "ABMForge" in citation
    assert abmforge.__version__ in citation
    assert "Apache-2.0" in citation


def test_cite_command_outputs_text(capsys) -> None:  # type: ignore[no-untyped-def]
    main(["cite"])

    captured = capsys.readouterr()

    assert "ABMForge" in captured.out
    assert "CITATION.cff" in captured.out


def test_cite_command_outputs_bibtex(capsys) -> None:  # type: ignore[no-untyped-def]
    main(["cite", "--format", "bibtex"])

    captured = capsys.readouterr()

    assert "@software{uludag_abmforge_2026" in captured.out
    assert abmforge.__version__ in captured.out


def test_info_command_mentions_repository(capsys) -> None:  # type: ignore[no-untyped-def]
    main(["info"])

    captured = capsys.readouterr()

    assert "ABMForge" in captured.out
    assert "Repository:" in captured.out


def test_format_citation_preserves_unicode_author_name() -> None:
    citation_text = format_citation("text")
    citation_bibtex = format_citation("bibtex")

    assert "Fatih Uludağ" in citation_text
    assert "Fatih Uludağ" in citation_bibtex
    assert "Fatih Uluda?" not in citation_text
    assert "Fatih Uluda?" not in citation_bibtex
