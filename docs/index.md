# ABMForge Documentation

ABMForge is a lightweight, reproducible, experiment-native agent-based modeling framework for Python.

The framework is designed for:

* researchers
* educators
* model developers
* data scientists
* students learning agent-based modeling

## Core Principles

ABMForge is built around four principles:

### Reproducibility

Simulation runs should be repeatable through explicit seeds, run metadata, manifests, and snapshots.

### Experiment-Native Design

Experiments are first-class concepts rather than afterthoughts.

### Dataset-First Outputs

Simulation outputs should be easy to analyze using standard data tools.

### Lightweight Python Architecture

The core framework should remain easy to understand and extend.

## Main Components

### Core Modeling

* Agent
* Model
* AgentCollection

### Spaces

* GridWorld
* NetworkSpace
* ContinuousSpace
* GISSpace

### Scheduling

* SequentialActivation
* RandomActivation
* SimultaneousActivation
* StagedActivation

### Experiments

* Scenario
* Experiment
* ParameterGrid
* ExperimentResult

### Analysis

* SensitivityAnalysis
* SALib integration

### Visualization

* plot_timeseries
* plot_multiple_runs
* plot_grid

### Replay

* Snapshot export
* Snapshot import

## Example Gallery

ABMForge currently includes:

* Wealth Model
* Schelling Segregation
* SIR Epidemic
* Sugarscape
* Parameter Sweep
* GIS Example

## Recommended Reading Order

1. Getting Started
2. First Model
3. Spaces
4. Scheduling
5. Experiments
6. Visualization
7. Analysis
8. GIS
