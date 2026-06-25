# Roadmap

ABMForge is currently an alpha-stage research software project.

The near-term goal is not to add many unrelated modelling features. The priority
is to make the existing experiment, dataset, archive, documentation, and release
workflow consistent, testable, and useful for researchers.

## Completed foundation

ABMForge already includes:

- core Agent and Model abstractions;
- agent collections and lifecycle records;
- grid, network, continuous, and lightweight GIS spaces;
- sequential, random, simultaneous, and staged activation;
- event queue and event ownership support;
- Scenario and Experiment abstractions;
- deterministic seed sequences and replicate plans;
- run, model, agent, event, lifecycle, and error records;
- JSON, CSV, and optional Parquet outputs;
- experiment archive helpers;
- archive validation and summary helpers;
- CLI commands for run, experiment, validate, summarize, report, cite, and new;
- built-in project templates;
- ODD documentation helpers;
- sensitivity analysis helpers;
- example models and model zoo entries;
- CI checks for tests, linting, typing, docs, and package smoke tests.

## 0.2.x alpha focus

- Fix user-facing documentation and CLI inconsistencies.
- Align README, citation metadata, CodeMeta, and CLI citation output.
- Make documentation examples executable in CI.
- Improve getting started and researcher onboarding pages.
- Keep public APIs explicitly marked as alpha.

## 0.3.x alpha focus

- Unify single-run and multi-run experiment outputs under one archive contract.
- Define Experiment Archive Specification v1.
- Strengthen archive validation and run indexing.
- Improve experiment reports and failure summaries.
- Add a canonical end-to-end reproducible research study.

## 0.4.x alpha focus

- Improve reproducibility conformance checks.
- Extend manifest metadata for source, inputs, command, and environment capture.
- Add migration support for archive and schema versions.
- Improve Parquet integrity checks.

## 0.5.x alpha focus

- Add resumable experiment execution.
- Add local parallel execution through an executor abstraction.
- Improve bounded-memory storage for long experiments.
- Expand verified model zoo examples.

## Beta readiness

ABMForge should not be considered beta-ready until:

- pip-based installation is tested from built distributions;
- documentation examples run in CI;
- unified experiment archives are implemented;
- public API stability rules are documented;
- a canonical reproducible study exists;
- Python 3.10-3.13 are tested;
- basic Linux, macOS, and Windows smoke checks exist.

## 1.0.0 readiness

ABMForge 1.0 should require:

- stable public API contracts;
- versioned archive and dataset schemas;
- migration guides;
- plugin and extension guides;
- formal release and citation workflow;
- DOI-backed archived release;
- benchmark and comparison documentation;
- evidence of real research use.
