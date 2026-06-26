# ABMForge Benchmark Suite

This directory contains lightweight benchmark tooling for ABMForge.

The current suite is intentionally small and conservative. It is designed to
make benchmark execution repeatable before adding larger performance claims.

## Commands

List available cases:

```bash
python benchmarks/run_reference_suite.py --list
```

Run the quick suite:

```bash
python benchmarks/run_reference_suite.py --quick
```

Write results to a file:

```bash
python benchmarks/run_reference_suite.py --quick --repeat 3 --output outputs/benchmarks/reference_suite.json
```

## Current Case Types

The first reference case exercises the documented CLI workflow:

```text
scenario run -> archive validate -> archive summarize
```

Future cases should add API-level benchmarks, experiment benchmarks, archive
validation benchmarks, and comparison baselines.

## Result Format

The runner writes JSON with:

- `schema_version`;
- `created_at`;
- `environment`;
- `cases`;
- `results`.

The schema is intentionally simple so that future scripts can compare benchmark
runs without depending on a database or external service.

## Guidance

Do not use this scaffold to make performance claims yet.

Use it to detect obvious slowdowns, document benchmark methodology, prepare
future comparison experiments, and support publication-readiness work.
