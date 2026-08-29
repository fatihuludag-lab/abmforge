from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "experiment-recovery.md"


def test_experiment_recovery_doc_defines_fail_closed_identity_contract() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "run-identity-v2" in text
    assert "execution-fingerprint-v3" in text
    assert "fail-closed" in text
    assert "model-source SHA-256" in text
    assert "Legacy archive behavior" in text
    assert "programmatic `stop_when` callbacks" in text


def test_experiment_recovery_doc_states_v3_scope_limitations() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "undeclared input files" in text
    assert "dependency or interpreter versions" in text
    assert "recorder configuration" in text
    assert "necessary, but not sufficient" in text


def test_experiment_recovery_doc_is_linked_from_public_docs() -> None:
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    experiments = (ROOT / "docs" / "experiments.md").read_text(encoding="utf-8")
    archive_format = (ROOT / "docs" / "archive-format.md").read_text(encoding="utf-8")
    archive_spec = (ROOT / "docs" / "experiment-archive-v1.md").read_text(encoding="utf-8")
    api = (ROOT / "docs" / "api.md").read_text(encoding="utf-8")

    assert "Safe Experiment Recovery: experiment-recovery.md" in nav
    assert "[Safe Experiment Recovery](experiment-recovery.md)" in experiments
    assert "execution_fingerprint" in archive_format
    assert "run-identity-v2" in archive_format
    assert "execution-fingerprint-v3" in archive_format
    assert "execution-fingerprint-v3" in experiments
    assert "execution-fingerprint-v3" in archive_spec
    assert "ExecutionFingerprintV3" in api
    assert "ExecutionFingerprintV1" in api
    assert "ExecutionFingerprintV2" in api
