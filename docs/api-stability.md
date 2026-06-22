# API Stability

ABMForge is alpha-stage software. Public APIs may still evolve before `v1.0.0`.

This document describes the intended stability level of the main user-facing APIs.
As a rule, APIs exported from the root `abmforge` package are public. APIs that
are not exported from `abmforge.__init__` should be considered internal unless a
documentation page explicitly says otherwise.

## Stability Levels

### Stable Candidate

APIs in this category are expected to remain mostly stable until `v1.0.0`.
Minor additions are allowed. Breaking changes should be avoided unless strongly
justified by correctness, reproducibility, or API coherence.

### Experimental

APIs in this category may change as the framework evolves.

### Internal

Internal APIs are not intended for direct user use.

## Stable Candidate APIs

### Core

- `Agent`
- `Model`
- `AgentCollection`

### Experiment

- `Scenario`
- `Experiment`
- `ExperimentResult`
- `ParameterGrid`
- `RunResult`
- `ExperimentArchive`

### Spaces

- `GridWorld`
- `NetworkSpace`
- `ContinuousSpace`

`GISSpace` is available from the root package but should be treated as
experimental until the GIS space contract is strengthened.

### Data

- `Dataset`
- `Recorder`
- `DatasetSchemaV1`
- `DATASET_SCHEMA_VERSION`
- `SchemaValidationError`

### Events

- `Event`
- `EventQueue`

### Scheduling

- `SequentialActivation`
- `RandomActivation`
- `SimultaneousActivation`
- `StagedActivation`

### Visualization

- `plot_timeseries`
- `plot_multiple_runs`
- `plot_grid`

### Analysis

- `SensitivityAnalysis`
- `SALibProblem`
- `sample_sobol`
- `analyze_sobol`
- `sample_morris`
- `analyze_morris`

## Experimental APIs

The following areas are considered experimental:

- full replay and model reconstruction
- snapshot restoration beyond basic state reconstruction
- `GISSpace` behavior beyond point-coordinate use
- plugin architecture
- advanced storage backends
- high-performance columnar agent backends
- advanced calibration interfaces
- future AI-enabled ABM workflow interfaces

## Breaking Change Policy

Before `v1.0.0`, breaking changes may occur, but they should follow these rules:

1. Prefer additive changes.
2. Avoid renaming public classes and methods unless necessary.
3. Deprecate before removing when practical.
4. Document migration steps.
5. Update examples and tests in the same pull request.

## v1.0.0 Criteria

ABMForge should reach `v1.0.0` only when:

- the public API is documented,
- core examples are stable,
- CI passes across supported Python versions,
- documentation is published,
- test coverage remains above the target threshold,
- release notes clearly describe supported features,
- and archive/reproducibility guarantees are explicitly defined.
