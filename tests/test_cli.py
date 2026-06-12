import pytest

from abmforge import __version__
from abmforge.cli.main import main


def test_cli_version(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["abmforge", "--version"])

    main()

    captured = capsys.readouterr()

    assert __version__ in captured.out


def test_cli_info(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["abmforge", "info"])

    main()

    captured = capsys.readouterr()

    assert "ABMForge" in captured.out
    assert __version__ in captured.out
    assert "Core objects" in captured.out


def test_cli_help(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["abmforge"])

    main()

    captured = capsys.readouterr()

    assert "usage:" in captured.out


def test_cli_unknown_command(monkeypatch):
    monkeypatch.setattr("sys.argv", ["abmforge", "unknown"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
