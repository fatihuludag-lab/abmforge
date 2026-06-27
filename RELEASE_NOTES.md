# ABMForge Alpha Development Notes

Current development version: `0.3.0a1`.

ABMForge is currently alpha-stage research software. The current `main` branch
contains changes after the `v0.2.0a3` tag and should be treated as a development
state rather than a formal release artifact.

## Current main branch highlights

Recent development has focused on making ABMForge's research-software claims
more defensible before expanding the feature surface.

### Reproducibility and execution correctness

- `Scenario.run()` now respects model-internal `stop()` calls.
- `NetworkSpace` now preserves deterministic neighbor and agent iteration order.
- Snapshot agent restore is explicit and ID-safe.

### Archive integrity

- Archive creation refuses existing paths unless `overwrite=True` is explicit.
- Parquet archive validation checks table presence, readability, and manifest
  row-count consistency.

### Project metadata and positioning

- Public wording is being aligned with the current alpha-stage implementation.
- Version metadata is aligned across package, citation, and CodeMeta files.
- The project license file uses the canonical Apache License 2.0 text.

## Not a stable release

This development state does not yet imply:

- stable public APIs,
- self-contained experiment reconstruction,
- mature replay/checkpoint support,
- distributed experiment execution,
- full cross-platform validation beyond CI,
- or production-grade archive provenance.

## Recommended user interpretation

Use this version for local research software experiments, teaching prototypes,
model development, and reproducibility-oriented ABM workflow development. For
published or long-lived research workflows, preserve model source code, input
data, dependency specifications, and the execution environment alongside any
ABMForge archive.
