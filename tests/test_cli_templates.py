from __future__ import annotations

import json

from abmforge.cli.main import build_parser, main


def test_build_parser_includes_templates_command() -> None:
    help_text = build_parser().format_help()

    assert "templates" in help_text


def test_cli_templates_lists_builtin_templates(capsys) -> None:
    main(["templates"])

    captured = capsys.readouterr()

    assert "Available ABMForge project templates" in captured.out
    assert "- epidemic:" in captured.out
    assert "- grid:" in captured.out
    assert "- network:" in captured.out
    assert "- policy:" in captured.out
    assert "- resource:" in captured.out
    assert "- segregation:" in captured.out
    assert "abmforge new my-study --template <template>" in captured.out


def test_cli_templates_json_output(capsys) -> None:
    main(["templates", "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert payload == [
        {
            "name": "epidemic",
            "description": "Grid-based SIR epidemic ABM study template for researcher workflows.",
        },
        {
            "name": "grid",
            "description": "Minimal grid-based ABM study template for researcher workflows.",
        },
        {
            "name": "network",
            "description": "Network-based diffusion ABM study template for researcher workflows.",
        },
        {
            "name": "policy",
            "description": ("Policy intervention ABM study template for researcher workflows."),
        },
        {
            "name": "resource",
            "description": (
                "Renewable resource competition ABM study template for researcher workflows."
            ),
        },
        {
            "name": "segregation",
            "description": (
                "Schelling-style spatial segregation ABM study template for researcher workflows."
            ),
        },
    ]
