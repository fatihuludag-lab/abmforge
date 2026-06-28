# API Stability Policy

ABMForge is currently alpha-stage research software.

This document defines how public APIs, archive formats, dataset schemas, and
deprecations should be handled while the project moves toward beta and 1.0.

## Status

Current status:

```text
alpha
```

Alpha status means:

- public APIs may still change;
- archive and dataset contracts may still evolve;
- breaking changes are allowed when they materially improve the research workflow;
- breaking changes should be documented and tested;
- users should pin exact versions or commits for published research.

## Goals

The API stability policy aims to:

1. reduce accidental breakage;
2. make public interfaces explicit;
3. separate stable, provisional, and experimental APIs;
4. document breaking changes before releases;
5. provide migration guidance where practical;
6. protect published research workflows from silent drift.

## API Stability Levels

ABMForge uses three stability levels.

### Stable

A stable API is intended to remain compatible within a major release line.

Stable APIs should have:

- documentation;
- type hints where practical;
- tests;
- changelog coverage for changes;
- deprecation warnings before removal.

During alpha, very few APIs should be marked stable.

### Provisional

A provisional API is intended for normal users but may still change before beta
or 1.0.

Most user-facing ABMForge APIs are currently provisional.

Examples include:

- `Agent`;
- `Model`;
- `Scenario`;
- `Experiment`;
- `Dataset`;
- `ExperimentArchive`;
- built-in schedulers;
- built-in spaces;
- CLI commands.
- typed-agent protocols such as `AgentLike`, `SteppableAgent`, and `StatefulAgent`.

Provisional APIs should not be changed casually. When they change, the reason
should be documented.

### Experimental

An experimental API is intended for exploration and may change without a long
deprecation window.

Experimental APIs should be clearly marked in documentation.

Examples may include:

- new storage backends;
- replay internals;
- plugin prototypes;
- calibration prototypes;
- future external-framework adapters.

## Public API Surface

The public API includes:

- documented imports from `abmforge`;
- documented submodules under `abmforge.core`;
- documented submodules under `abmforge.experiment`;
- documented submodules under `abmforge.data`;
- documented CLI commands;
- documented archive and dataset formats.

Internal helpers are not public API simply because they are importable.

Names beginning with `_` are internal unless explicitly documented otherwise.

## CLI Stability

The CLI is part of the public user interface.

Stable or provisional CLI behavior includes:

- command names;
- required arguments;
- output paths;
- exit codes;
- documented JSON output fields;
- archive validation behavior.

CLI changes that affect scripts should be treated as compatibility-relevant.

## Archive and Dataset Compatibility

Archive and dataset compatibility is especially important because researchers
may cite or share generated artifacts.

Changes to any of the following should be considered compatibility-relevant:

- archive directory layout;
- `manifest.json`;
- `dataset_schema.json`;
- `run_index.json`;
- standard dataset table names;
- standard dataset column names;
- logical meaning of standard fields;
- validation behavior;
- report output file names used by documented workflows.

When possible, archive readers should detect unsupported versions clearly rather
than failing with unclear parsing errors.

## Deprecation Policy

A deprecated public API should:

1. continue to work for at least one subsequent minor alpha release when practical;
2. emit a clear warning when used;
3. identify the replacement API;
4. be documented in the changelog;
5. include tests for the warning behavior.

During alpha, immediate removal may still be acceptable for unsafe or clearly
broken APIs, but the reason should be documented.

## Breaking Changes

Breaking changes should include:

- motivation;
- affected APIs or files;
- migration guidance;
- test coverage;
- documentation updates.

Examples of breaking changes:

- renaming public classes or functions;
- changing required constructor arguments;
- changing CLI command behavior;
- changing archive or dataset schema semantics;
- removing documented fields;
- changing default reproducibility or randomness behavior.

## Versioning Expectations

Before beta:

- breaking changes are allowed but should be explicit;
- release notes should identify breaking changes;
- users should pin versions for research artifacts.

After beta:

- public APIs should change more slowly;
- deprecations should be preferred over immediate removals;
- archive and dataset migration paths should be provided for important changes.

At 1.0:

- stable public APIs should have stronger compatibility guarantees;
- archive and dataset format versions should have documented migration rules;
- breaking changes should require a major version bump.

## Research Reproducibility Guidance

For published research, users should record:

- ABMForge version;
- Python version;
- operating system;
- exact source commit when using an unreleased version;
- scenario or experiment configuration;
- archive manifest;
- dataset schema version;
- input data hashes when applicable.

ABMForge can help capture some of this metadata, but users remain responsible
for preserving source code, input data, and execution environments until higher
reproducibility tiers are fully implemented.

## Maintainer Checklist for API Changes

Before merging a public API change, check:

- Is this public, provisional, experimental, or internal?
- Does documentation need to change?
- Does a migration note need to be added?
- Does the changelog need an entry?
- Is a deprecation warning more appropriate than removal?
- Does the change affect archive or dataset compatibility?
- Do executable documentation examples still pass?
- Do package smoke tests still pass?

## Current Policy Summary

```text
Stable APIs: limited
Provisional APIs: most documented user-facing APIs
Experimental APIs: replay, plugin, calibration, and adapter prototypes
Internal APIs: undocumented helpers and underscore-prefixed names
```

This policy should be revisited before the first beta release.

## Machine-readable API declarations

The current top-level import contract is declared in `abmforge.api`:

```python
from abmforge.api import (
    API_STABILITY_LEVELS,
    EXPERIMENTAL_API,
    PROVISIONAL_API,
    PUBLIC_API,
    STABLE_ALPHA_API,
)
```

`PUBLIC_API` is the authoritative source for `abmforge.__all__`. The stability
groups must partition `PUBLIC_API`, and `tests/test_public_api.py` verifies this
contract. Any pull request that adds, removes, or reclassifies a top-level import
should update `abmforge.api`, this policy, and the changelog together.

The current groups mean:

- `STABLE_ALPHA_API`: core imports that should not disappear accidentally during
  the alpha line.
- `PROVISIONAL_API`: user-facing imports that are documented but may still
  evolve before beta or 1.0.
- `EXPERIMENTAL_API`: optional, replay, analysis, or visualization helpers that
  can change more freely while their contracts mature.
