# API Stability

ABMForge is currently alpha-stage software. Public APIs may still evolve before v1.0.0.

This document defines the intended stability level of the main public APIs.

## Stability Levels

### Stable Candidate

APIs in this category are expected to remain mostly stable until v1.0.0.

Minor additions are allowed, but breaking changes should be avoided unless strongly justified.

### Experimental

APIs in this category may change as the framework evolves.

### Internal

APIs in this category are not intended for direct user use.

## Stable Candidate APIs

### Core

- Agent
- Model
- AgentCollection

### Experiment

- Scenario
- Experiment
- ExperimentResult
- ParameterGrid
- RunResult

### Spaces

- GridWorld
- NetworkSpace
- ContinuousSpace
- GISSpace

### Data

- Dataset
- Recorder

### Events

- Event
- EventQueue

### Scheduling

- SequentialActivation
- RandomActivation
- SimultaneousActivation
- StagedActivation

### Replay

- write_snapshot
- read_snapshot

### Visualization

- plot_timeseries
- plot_multiple_runs
- plot_grid

### Analysis

- SensitivityAnalysis
- SALibProblem
- sample_sobol
- analyze_sobol
- sample_morris
- analyze_morris

## Experimental APIs

The following areas are considered experimental:

- full replay and model reconstruction
- plugin architecture
- advanced storage backends
- high-performance columnar agent backends
- advanced calibration interfaces
- GIS integrations beyond point coordinates

## Internal APIs

Anything not exported from `abmforge.__init__` should be considered internal unless documented otherwise.

## Breaking Change Policy

Before v1.0.0, breaking changes may occur, but they should follow these rules:

1. Prefer additive changes.
2. Avoid renaming public classes and methods.
3. Deprecate before removing when possible.
4. Document migration steps.
5. Update examples and tests in the same pull request.

## v1.0.0 Criteria

ABMForge should reach v1.0.0 only when:

- the public API is documented
- core examples are stable
- CI passes across supported Python versions
- documentation is published
- test coverage remains above the target threshold
- release notes clearly describe supported features
