# ABMForge Alpha Development Notes

Current development version: `0.3.0a2.dev0`.

ABMForge is currently alpha-stage research software. Version `0.3.0a1` was
published as the first production PyPI alpha release on 2026-06-30. The current
`main` branch contains post-release changes and is intentionally versioned
`0.3.0a2.dev0` so that source checkouts cannot be confused with the immutable
`0.3.0a1` release artifact.

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

## Current main is not a formal release

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
