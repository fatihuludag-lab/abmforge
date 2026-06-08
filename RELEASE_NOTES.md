# ABMForge 0.1.0a1 Release Notes

This alpha patch keeps the first release installable on systems using Python 3.10.

## Changed since 0.1.0a0

- Lowered `requires-python` from `>=3.11` to `>=3.10`.
- Replaced Python 3.11-only `datetime.UTC` with Python 3.10-compatible `timezone.utc`.
- Updated Ruff and mypy configuration targets to Python 3.10.

## Included

- Installable `abmforge` Python package.
- `Model`, `Agent`, and `AgentCollection` core abstractions.
- Deterministic model-level random number generator.
- `GridWorld` with placement, movement, removal, and neighbor queries.
- `EventQueue` with schedule, cancel, owner, tags, and event logging.
- `Recorder` and in-memory `Dataset`.
- `Scenario` and `RunResult` for reproducible local runs.
- Minimal sequential `Experiment` runner.
- CLI entry point: `abmforge`.
- Wealth model example.
- CI workflow template.
- Initial test suite.

## Not included yet

- TestPyPI/PyPI upload.
- Multiprocessing runner.
- Storage backends beyond in-memory JSON writing.
- Plugin discovery.
- Full visualization dashboard.
- Columnar agent backend.
