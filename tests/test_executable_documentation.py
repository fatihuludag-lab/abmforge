from __future__ import annotations

import os
import re
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

EXECUTABLE_PYTHON_BLOCK = re.compile(
    r"<!--\s*abmforge:execute-python\s*-->\s*```python\s*(.*?)\s*```",
    re.DOTALL,
)

CRITICAL_DOCS = [
    ROOT / "README.md",
    ROOT / "docs" / "getting-started.md",
    ROOT / "docs" / "odd-export.md",
]


def _extract_executable_python_blocks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [textwrap.dedent(block).strip() for block in EXECUTABLE_PYTHON_BLOCK.findall(text)]


@pytest.mark.parametrize("doc_path", CRITICAL_DOCS, ids=lambda path: path.name)
def test_critical_docs_have_marked_executable_python_examples(doc_path: Path) -> None:
    blocks = _extract_executable_python_blocks(doc_path)

    assert blocks, f"{doc_path.relative_to(ROOT)} has no executable Python examples"


@pytest.mark.parametrize("doc_path", CRITICAL_DOCS, ids=lambda path: path.name)
def test_marked_python_documentation_examples_execute(
    doc_path: Path,
    tmp_path: Path,
) -> None:
    blocks = _extract_executable_python_blocks(doc_path)
    original_cwd = Path.cwd()

    try:
        for index, code in enumerate(blocks):
            workdir = tmp_path / doc_path.stem / str(index)
            workdir.mkdir(parents=True, exist_ok=True)
            os.chdir(workdir)

            namespace: dict[str, object] = {"__name__": "__main__"}
            exec(compile(code, str(doc_path), "exec"), namespace)
    finally:
        os.chdir(original_cwd)


def test_getting_started_no_longer_uses_placeholder_model_name() -> None:
    text = (ROOT / "docs" / "getting-started.md").read_text(encoding="utf-8")

    assert "MyModel" not in text
    assert "WealthModel" in text
    assert "Scenario(" in text
    assert "Experiment(" in text
