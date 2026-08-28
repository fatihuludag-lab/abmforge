from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_source_input_provenance_page_documents_contracts() -> None:
    text = (ROOT / "docs" / "source-input-provenance.md").read_text(encoding="utf-8")

    required = (
        "source-repository-provenance-v1",
        "input-artifact-v1",
        'scope": "model-source',
        "input_artifact_count",
        "from_run_result()",
        "from_dataset()",
        "Path.cwd()",
        "symlink escape",
        "execution-fingerprint-v2",
    )
    for term in required:
        assert term in text


def test_reproducibility_manifest_docs_include_source_and_inputs() -> None:
    text = (ROOT / "docs" / "reproducibility-manifest-v1.md").read_text(encoding="utf-8")

    assert "Model-source Git provenance" in text
    assert "Input artifact inventory and checksums" in text
    assert "input_artifacts" in text
    assert "input_artifact_count" in text
    assert "source-repository-provenance-v1" in text


def test_public_api_documents_provenance_types() -> None:
    text = (ROOT / "docs" / "api.md").read_text(encoding="utf-8")

    assert "SourceRepositoryProvenanceV1" in text
    assert "InputArtifactProvenanceV1" in text
    assert "from abmforge.repro import" in text
    assert "input_root" in text


def test_provenance_page_is_in_navigation_and_changelog() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert "Source and Input Provenance: source-input-provenance.md" in nav
    assert "source-repository-provenance-v1" in changelog
    assert "input-artifact-v1" in changelog
