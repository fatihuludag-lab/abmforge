# Changelog

All notable changes to this project are documented in this file.

ABMForge is still alpha-stage software. APIs, archive formats, replay/snapshot
behavior, and research-workflow guarantees may change before a stable release.

## Unreleased

Current development version: `0.2.0a4.dev0`.

### Fixed

- Respect `Model.stop()` calls made during `Scenario.run()`.
- Make `NetworkSpace` neighbor and agent iteration order deterministic across
  Python hash seeds.
- Make snapshot agent restore explicit through an `agent_classes` registry.
- Keep integer agent ID allocation safe after restoring or manually adding agents.
- Refuse to create experiment archives at existing paths unless `overwrite=True`
  is explicit.
- Validate Parquet archive table presence, readability, and row counts against
  manifest `record_counts`.

### Changed

- Soften alpha-stage positioning claims from "reproducible by default" toward
  "reproducibility-oriented".
- Make CI mypy checks use the active matrix Python version.
- Replace the project `LICENSE` file with the canonical Apache License 2.0 text.

### Notes

- The current main branch is newer than the `v0.2.0a3` tag.
- This development version is not a GitHub release artifact.
- Independent reproduction still requires preserving model source code, input
  data, dependency state, and execution environment.

## 0.2.0a3 - 2026-06-16

### Added

- Dataset Schema V1 and dataset validation.
- Experiment archive support.
- Scenario YAML workflow.
- Reproducibility manifest support.
- ODD export support.
- Initial model-zoo examples for Schelling and SIR workflows.
- Citation metadata files.

### Notes

- This was a tagged alpha milestone, not a GitHub release artifact.

## 0.1.0a1 - 2026-06-08

### Changed

- Lowered package requirement from Python `>=3.11` to Python `>=3.10`.
- Replaced Python 3.11-only `datetime.UTC` usage with Python 3.10-compatible
  `timezone.utc`.
- Updated Ruff and mypy targets to Python 3.10.

## 0.1.0a0 - First alpha release

### Added

- Installable Python package skeleton.
- `Model`, `Agent`, and `AgentCollection` core classes.
- Deterministic model-level RNG.
- Basic `GridWorld` with placement, movement, removal, and neighbor queries.
- Basic `EventQueue` with scheduling, cancellation, owner, tags, and event
  logging.
- `Recorder` and in-memory `Dataset`.
- `Scenario` and `RunResult` for reproducible local runs.
- Minimal `Experiment` runner.
- `abmforge` CLI with version and package info commands.
- Wealth model example.
- Initial pytest test suite.
