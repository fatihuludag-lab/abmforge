# ABMForge Documentation

ABMForge is a lightweight, reproducible, experiment-native agent-based modeling framework for Python.

It is designed for researchers, educators, model developers, data scientists, and students who want to build agent-based simulations that are reproducible, analyzable, and extensible.

## Core Principles

ABMForge is built around four principles:

### Reproducibility

Simulation runs should be repeatable through explicit seeds, run metadata, manifests, and snapshots.

### Experiment-Native Design

Experiments are first-class concepts rather than afterthoughts.

### Dataset-First Outputs

Simulation outputs should be easy to analyze using standard data tools.

### Lightweight Python Architecture

The core framework should remain easy to understand, easy to test, and easy to extend.

## Main Components

### Core Modeling

- `Agent`
- `Model`
- `AgentCollection`

### Spaces

- `GridWorld`
- `NetworkSpace`
- `ContinuousSpace`
- `GISSpace`

### Scheduling

- `SequentialActivation`
- `RandomActivation`
- `SimultaneousActivation`
- `StagedActivation`

### Experiments

- `Scenario`
- `Experiment`
- `ParameterGrid`
- `ExperimentResult`

### Data and Reproducibility

- `Recorder`
- `Dataset`
- CSV export
- JSON/JSONL export
- Reproducibility manifest
- Snapshot read/write helpers

### Analysis

- `SensitivityAnalysis`
- Optional SALib integration
- Sobol sampling
- Morris sampling

### Visualization

- `plot_timeseries`
- `plot_multiple_runs`
- `plot_grid`

## Example Gallery

ABMForge currently includes:

- Wealth model
- Schelling segregation
- SIR epidemic
- Sugarscape
- Parameter sweep
- GIS example

## Recommended Reading Order

1. Getting Started
2. First Model
3. Spaces
4. Scheduling
5. Experiments
6. Visualization
7. Analysis
8. Replay
9. GIS
10. API Reference
