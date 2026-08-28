# Changelog



## [0.3.0a1] - 2026-06-30

### Highlights

- Published ABMForge's first production PyPI alpha release.
- Added production PyPI trusted-publishing gate documentation and workflow checks.
- Prepared the user-facing install path for `pip install abmforge`.

### Release Record

- Release tag: `v0.3.0a1`.
- Released package version: `0.3.0a1`.
- Production PyPI publishing used manual workflow dispatch, a tag ref, and `pypi` environment approval.
- The release path included a TestPyPI dry run before production publishing.

### Known Limitations

- ABMForge remains alpha-stage research software.
- Most public APIs are provisional.
- Archive and dataset formats may still evolve before beta or 1.0.

## [0.2.0a4.dev0] - Unreleased

### Highlights

- Continued release-readiness work for ABMForge as alpha-stage research software.
- Strengthened the project around reproducible workflows, packaging, documentation, and publication preparation.

### Added

- Conservative release workflow for build artifacts and optional TestPyPI publishing.
- Release metadata and changelog checklist.
- Community health files, issue templates, and pull request template.
- Public API stability policy.
- Expanded public API reference aligned with root package exports.
- Benchmark reference suite scaffold.
- Researcher quickstart for install, scenario execution, archive validation, summary, report, and reproducible study workflow.

### Changed

- Improved release preparation guidance and strict release metadata checks.
- Clarified alpha-stage API, archive, and research validity expectations.

### Validation

- Main CI matrix covers supported Python versions.
- Package smoke workflow validates built wheel behavior.
- Release metadata can be checked with `python scripts/check_release_metadata.py --strict`.
- Documentation examples and key researcher workflows are covered by tests.

### Known Limitations

- ABMForge remains alpha-stage research software.
- Most public APIs are provisional.
- Benchmark support is a scaffold and does not yet support performance claims.
- Production PyPI publishing and formal DOI archiving require separate maintainer action.

All notable changes to this project are documented in this file.

ABMForge is still alpha-stage software. APIs, archive formats, replay/snapshot
behavior, and research-workflow guarantees may change before a stable release.

## Unreleased

Current development version: `0.3.0a2.dev0`.

### Added

- Add `source-repository-provenance-v1` so run-result manifests discover Git
  metadata from the executed model's defining source file rather than the
  process current working directory.
- Add `input-artifact-v1` records with portable paths, byte sizes, SHA-256
  checksums, root-containment checks, and a separate manifest input inventory.

- Add `ExecutionFingerprintV1` with model-source SHA-256, canonical parameter
  hashing, versioned serialization, and digest integrity checks.
- Persist execution fingerprints in dataset run metadata and `run_index.json`.
- Document fail-closed recovery, legacy archive behavior, and the current
  fingerprint scope.

### Fixed

- Prevent completed runs from being reused after the model source changes.
- Reject legacy, incomplete, unsupported, tampered, or metadata-inconsistent
  recovery identities instead of silently suppressing planned runs.

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

- Upgrade recovery matching from `run-identity-v1` to `run-identity-v2` with
  `execution-fingerprint-v1`; older identities remain readable but are not
  automatically reusable.
- Soften alpha-stage positioning claims from "reproducible by default" toward
  "reproducibility-oriented".
- Make CI mypy checks use the active matrix Python version.
- Replace the project `LICENSE` file with the canonical Apache License 2.0 text.

### Notes

- The current main branch is newer than the `v0.3.0a1` release.
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
