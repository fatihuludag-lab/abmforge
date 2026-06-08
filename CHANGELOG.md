# Changelog

All notable changes to this project will be documented in this file.

## 0.1.0a1 - Python 3.10 compatibility patch

### Changed

- Lowered package requirement from Python `>=3.11` to Python `>=3.10`.
- Replaced Python 3.11-only `datetime.UTC` usage with Python 3.10-compatible `timezone.utc`.
- Updated Ruff and mypy targets to Python 3.10.

## 0.1.0a0 - First alpha release

### Added

- Installable Python package skeleton.
- `Model`, `Agent`, and `AgentCollection` core classes.
- Deterministic model-level RNG.
- Basic `GridWorld` with placement, movement, removal, and neighbor queries.
- Basic `EventQueue` with scheduling, cancellation, owner, tags, and event logging.
- `Recorder` and in-memory `Dataset`.
- `Scenario` and `RunResult` for reproducible runs.
- Minimal `Experiment` runner.
- `abmforge` CLI with version and package info commands.
- Wealth model example.
- Initial pytest test suite.
