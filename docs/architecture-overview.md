# Architecture Overview

ABMForge is an alpha-stage, Python-first framework for building agent-based modelling workflows around models, scenarios, experiments, datasets, archives, and reproducibility metadata.

This page gives a high-level map of the current architecture. It is intended for new users, reviewers, and contributors who want to understand how the main modules fit together before reading the API reference or source code.

ABMForge is intentionally lightweight. The current architecture focuses on research software workflows rather than large-scale distributed simulation, mature checkpoint/replay, or full production-grade runtime guarantees.

## Design goals

ABMForge currently emphasizes:

- small, inspectable Python components;
- scenario- and experiment-oriented model execution;
- dataset-first outputs for analysis and review;
- explicit metadata for reproducibility-oriented workflows;
- a documented distinction between stable public APIs, experimental APIs, and internal implementation details.

The framework should currently be understood as strong alpha-stage research software. Some APIs are intended to stabilize over time, while experimental and internal modules may change more frequently.

## Main modules

The package is organized around a small number of responsibilities.

| Module | Main responsibility |
| --- | --- |
| `abmforge.core` | Core modelling abstractions such as agents, models, collections, status, and lifecycle behaviour. |
| `abmforge.world` | Space/environment abstractions such as grid, network, continuous, and GIS-style spaces. |
| `abmforge.time` | Event and queue primitives for event-oriented workflows. |
| `abmforge.scheduling` | Activation strategies such as sequential, random, simultaneous, and staged scheduling. |
| `abmforge.data` | Recording, datasets, schema validation, and storage/export helpers. |
| `abmforge.experiment` | Scenarios, parameter grids, experiment execution, run results, and archive helpers. |
| `abmforge.analysis` | Lightweight analysis helpers and optional sensitivity-analysis integrations. |
| `abmforge.methods` | Methodological helpers such as ODD-oriented documentation/export support. |
| `abmforge.repro` | Reproducibility metadata, manifests, and snapshot-related helpers. |
| `abmforge.cli` | Command-line workflows for running, validating, summarizing, and citing projects. |

## Execution flow

A typical ABMForge workflow starts from either Python code or a scenario YAML file. The scenario creates a model, runs it with a seed and step configuration, records data, and optionally writes an archive.

```text
Scenario YAML / Scenario
        |
        v
Model construction
        |
        v
Scheduler / World / Agents
        |
        v
Model steps and recording
        |
        v
Recorder / Dataset
        |
        v
Experiment archive
        |
        v
Validate / Summarize / Analyze
```

The important architectural idea is that model execution and research outputs are linked. A run is not only a sequence of agent updates; it can also produce structured records, metadata, validation results, and archive files that are easier to inspect later.

## Core layer

The `core` layer contains the basic modelling objects.

`Agent` represents model entities. `Model` owns model state, agents, random state, lifecycle status, and run-level behaviour. `AgentCollection` helps manage groups of agents.

This layer should remain small and general. Domain-specific logic should normally live in user models, examples, model-zoo entries, or optional extensions rather than in the core package.

## World and scheduling layers

The `world` layer provides environment abstractions. Current space types include grid, network, continuous, and GIS-style spaces.

The `scheduling` layer controls how agents are activated. Scheduling is intentionally separate from the model so that a model can choose a suitable activation strategy without hard-coding the framework around one execution style.

Together these layers support common ABM patterns while keeping the model code explicit.

## Data layer

The `data` layer turns model execution into structured records.

Recorder and dataset components can capture model-level metrics, agent-level data, lifecycle records, events, and run metadata. Dataset schema and validation utilities help make outputs easier to check before downstream analysis.

ABMForge currently supports lightweight export and archive workflows. These are useful for research software review and reproducible experiment reporting, but they should not yet be presented as a mature, fully self-contained reconstruction system.

## Experiment layer

The `experiment` layer organizes repeated execution.

A `Scenario` represents a configured model run. An `Experiment` can combine parameters and seeds into multiple runs. `ParameterGrid` materializes parameter combinations so that experiment design is explicit and inspectable.

This layer is central to ABMForge's positioning: the framework is designed around computational experiments, not only one-off simulation scripts.

## Reproducibility layer

The `repro` layer records metadata that supports reproducibility-oriented workflows.

Current support includes run metadata, manifest-style documentation, snapshot helpers, and archive validation pieces. These features make runs easier to review, compare, and rerun under controlled conditions.

However, the current alpha architecture should not be described as guaranteeing full reconstruction by default. Stronger replay, checkpointing, dependency capture, and environment reconstruction remain future stabilization areas.

## CLI layer

The CLI exposes research workflow operations from the terminal.

Typical commands include running a scenario, validating an archive, summarizing results, and generating citation information. The CLI is intended to make common workflows repeatable without requiring users to write custom scripts for every step.

## Public, experimental, and internal APIs

ABMForge distinguishes between three levels of API stability.

### Public API

Public APIs are the preferred import paths documented for users. They are expected to be the most stable part of the framework.

Examples include top-level modelling, experiment, data, scheduling, and space abstractions that appear in documentation and examples.

### Experimental API

Experimental APIs are available for early use but may change as the framework matures. These are suitable for feedback, prototypes, and advanced users who can tolerate changes.

Examples may include newer storage, archive, reproducibility, GIS, or analysis helpers while their contracts are still being refined.

### Internal implementation details

Internal modules and private helpers are not part of the supported user-facing API. Contributors may edit them, but users should avoid depending on them directly.

As a rule of thumb:

```text
Documented import path + examples + API stability note = safer public use
Undocumented helper or private module = internal detail
New feature marked experimental = usable, but not yet stable
```

## Contributor guidance

When adding new functionality, prefer this order:

1. keep the public API small;
2. document the intended user workflow;
3. add focused tests around the behaviour;
4. avoid promising stronger reproducibility or stability than the code currently provides;
5. mark immature features as experimental until their contracts are clearer.

For documentation changes, prefer precise claims over broad claims. ABMForge should be described as reproducibility-oriented and experiment-native, not as a fully mature production or replay system.

## Current alpha boundaries

The current architecture is suitable for research-oriented alpha use, examples, teaching, reviewer inspection, and iterative model development.

Known boundaries include:

- public APIs are still stabilizing;
- replay and checkpoint workflows are not yet mature enough to be described as complete reconstruction systems;
- large-scale distributed execution is outside the current core scope;
- advanced GIS, storage, and analysis features may remain optional or experimental;
- performance guarantees should be measured with explicit benchmarks before being advertised.

These boundaries are intentional. They keep the project honest and make the next engineering steps easier to review.
