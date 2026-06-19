from pathlib import Path


def test_recording_docs_include_frequency_and_condition_examples() -> None:
    text = Path("docs/recording.md").read_text(encoding="utf-8")

    assert "record.metric" in text
    assert "record.agent" in text
    assert "every=5" in text
    assert "when=lambda model" in text
    assert "where=lambda agent" in text


def test_recording_docs_explain_why_frequency_matters() -> None:
    text = Path("docs/recording.md").read_text(encoding="utf-8")

    assert "reduce dataset size" in text
    assert "reproducible experiment archives" in text
