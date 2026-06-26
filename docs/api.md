# Public API Reference

**Status:** Alpha  
**Audience:** ABMForge users, contributors, reviewers, and downstream research projects.

This page documents the main public API exported by the root `abmforge` package
and the most important user-facing subpackages.

ABMForge is still alpha-stage software. Most documented APIs should be treated
as **provisional** until the project reaches beta or 1.0.

For compatibility expectations, see the API stability policy.

## Import Convention

Most user-facing projects should start with root imports:

```python
from abmforge import Agent, Experiment, Model, Scenario
```

Use subpackage imports when you need a specific scheduler, space, storage helper,
or method module.

## Stability Legend

| Label | Meaning |
| --- | --- |
| Stable | Intended to remain compatible within a major release line. Very limited during alpha. |
| Provisional | Intended for normal users, but may change before beta or 1.0. |
| Experimental | Useful for exploration; may change more quickly. |
| Internal | Not part of the documented public contract. |

## Core Modelling API

### `Agent`

**Status:** Provisional  
**Import:** `from abmforge import Agent`

Base class for individual agents.

Use it when defining agent-level state and behavior.

Typical responsibilities:

- hold agent attributes;
- implement `step()`;
- interact with other agents;
- read model parameters;
- use model-level random number generation;
- request spawn/remove behavior through the model or collection API.

### `Model`

**Status:** Provisional  
**Import:** `from abmforge import Model`

Base class for simulation models.

Typical responsibilities:

- initialize agents and spaces in `setup()`;
- advance the model in `step()`;
- own model parameters;
- own the model-level random number generator;
- configure recorders;
- manage simulation time and status.

Minimal shape:

```python
from abmforge import Agent, Model


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


class WealthModel(Model):
    def setup(self) -> None:
        self.agents.create(Person, n=10, wealth=0)

    def step(self) -> None:
        self.agents.do("step")
```

### `AgentCollection`

**Status:** Provisional  
**Import:** `from abmforge import AgentCollection`

Container and helper API for model agents.

Common uses:

- create agents;
- iterate over agents;
- apply methods to all agents;
- shuffle activation;
- filter or aggregate agent attributes;
- query by type or state.

## Experiment API

### `Scenario`

**Status:** Provisional  
**Import:** `from abmforge import Scenario`

A single model run configuration.

A scenario usually combines:

- model class;
- parameters;
- seed;
- number of steps;
- optional name;
- optional stop condition.

Example:

```python
from abmforge import Scenario

scenario = Scenario(
    model=WealthModel,
    parameters={"population": 10},
    seed=42,
    steps=5,
    name="baseline",
)

result = scenario.run()
```

### `Experiment`

**Status:** Provisional  
**Import:** `from abmforge import Experiment`

A multi-run experiment configuration.

Use it for:

- parameter sweeps;
- multiple seeds;
- stochastic replicates;
- comparative scenarios.

### `ExperimentResult`

**Status:** Provisional  
**Import:** `from abmforge import ExperimentResult`

Container for multi-run experiment results.

Typical uses:

- summarize runs;
- write CSV tables;
- collect model records;
- collect agent records;
- inspect failed runs.

### `RunResult`

**Status:** Provisional  
**Import:** `from abmforge import RunResult`

Container for one run result.

Typical fields include:

- run status;
- number of completed steps;
- dataset;
- stop reason;
- error information when a run fails.

### `ParameterGrid`

**Status:** Provisional  
**Import:** `from abmforge import ParameterGrid`

Helper for expanding parameter combinations.

### `ExperimentArchive`

**Status:** Provisional  
**Import:** `from abmforge import ExperimentArchive`

Directory-based experiment archive API.

Use it to:

- create archive roots;
- write scenario or experiment configuration files;
- write dataset tables;
- write schema and manifest files;
- validate archives;
- read run indexes.

### `ExperimentRegistry`

**Status:** Experimental  
**Import:** `from abmforge import ExperimentRegistry`

Registry helper for tracking experiment archive components and runs.

This API may evolve as archive migration and resumable experiments mature.

## Data and Recording API

### `Dataset`

**Status:** Provisional  
**Import:** `from abmforge import Dataset`

Structured simulation output container.

Standard logical tables include:

- `runs`;
- `model_records`;
- `agent_records`;
- `event_records`;
- `lifecycle_records`;
- `errors`.

### `Recorder`

**Status:** Provisional  
**Import:** `from abmforge import Recorder`

Model-attached recording helper.

Use it to record:

- model-level metrics;
- agent-level attributes;
- lifecycle events;
- event records;
- error records.

### `DatasetSchemaV1`

**Status:** Provisional  
**Import:** `from abmforge import DatasetSchemaV1`

Dataset schema validator and contract helper.

### `DATASET_SCHEMA_VERSION`

**Status:** Provisional  
**Import:** `from abmforge import DATASET_SCHEMA_VERSION`

Current dataset schema version identifier.

### `SchemaValidationError`

**Status:** Provisional  
**Import:** `from abmforge import SchemaValidationError`

Raised for dataset schema validation failures.

## Scheduling API

### `Scheduler`

**Status:** Provisional  
**Import:** `from abmforge import Scheduler`

Base scheduler abstraction.

### `SequentialActivation`

**Status:** Provisional  
**Import:** `from abmforge import SequentialActivation`

Activates agents in collection order.

### `RandomActivation`

**Status:** Provisional  
**Import:** `from abmforge import RandomActivation`

Activates agents in random order using the model-level random generator.

### `SimultaneousActivation`

**Status:** Provisional  
**Import:** `from abmforge import SimultaneousActivation`

Supports staged simultaneous-style activation.

### `StagedActivation`

**Status:** Provisional  
**Import:** `from abmforge import StagedActivation`

Runs named activation stages in order.

## Time and Event API

### `Event`

**Status:** Provisional  
**Import:** `from abmforge import Event`

Scheduled event object.

### `EventQueue`

**Status:** Provisional  
**Import:** `from abmforge import EventQueue`

Priority queue for scheduled events.

Time and event semantics are still evolving. Users should treat advanced event
behavior as provisional until the time model is finalized.

## Space API

### `GridWorld`

**Status:** Provisional  
**Import:** `from abmforge import GridWorld`

Grid-based space.

### `NetworkSpace`

**Status:** Provisional  
**Import:** `from abmforge import NetworkSpace`

Network-based space.

### `ContinuousSpace`

**Status:** Provisional  
**Import:** `from abmforge import ContinuousSpace`

Continuous coordinate space.

### `GISSpace`

**Status:** Experimental  
**Import:** `from abmforge import GISSpace`

Lightweight GIS-oriented space.

GIS support is intentionally limited during alpha.

## ODD and Methods API

### `ODDDocument`

**Status:** Provisional  
**Import:** `from abmforge import ODDDocument`

Structured ODD-style model documentation helper.

Generated ODD files are skeleton documents and require manual scientific review.

## Sensitivity Analysis API

### `SALibProblem`

**Status:** Experimental  
**Import:** `from abmforge import SALibProblem`

Problem specification helper for SALib-style sensitivity analysis.

### `SensitivityAnalysis`

**Status:** Experimental  
**Import:** `from abmforge import SensitivityAnalysis`

Sensitivity analysis helper.

### `sample_sobol`

**Status:** Experimental  
**Import:** `from abmforge import sample_sobol`

Generate Sobol samples.

### `analyze_sobol`

**Status:** Experimental  
**Import:** `from abmforge import analyze_sobol`

Analyze Sobol outputs.

### `sample_morris`

**Status:** Experimental  
**Import:** `from abmforge import sample_morris`

Generate Morris samples.

### `analyze_morris`

**Status:** Experimental  
**Import:** `from abmforge import analyze_morris`

Analyze Morris outputs.

## Reproducibility API

### `ReproducibilityManifest`

**Status:** Provisional  
**Import:** `from abmforge import ReproducibilityManifest`

Manifest helper for reproducibility metadata.

## Replay and Snapshot API

Replay is currently experimental.

### `write_snapshot`

**Status:** Experimental  
**Import:** `from abmforge import write_snapshot`

Write a model snapshot.

### `read_snapshot`

**Status:** Experimental  
**Import:** `from abmforge import read_snapshot`

Read a model snapshot.

### `snapshot_hash`

**Status:** Experimental  
**Import:** `from abmforge import snapshot_hash`

Compute a snapshot hash.

### `attach_snapshot_hash`

**Status:** Experimental  
**Import:** `from abmforge import attach_snapshot_hash`

Attach a hash to snapshot metadata.

### `link_snapshot`

**Status:** Experimental  
**Import:** `from abmforge import link_snapshot`

Link snapshot metadata to a run or archive.

### `validate_replay`

**Status:** Experimental  
**Import:** `from abmforge import validate_replay`

Validate replay behavior where supported.

### `ReplayValidationReport`

**Status:** Experimental  
**Import:** `from abmforge import ReplayValidationReport`

Report object for replay validation.

## Visualization API

Visualization helpers are optional convenience APIs.

### `plot_timeseries`

**Status:** Experimental  
**Import:** `from abmforge import plot_timeseries`

Plot a time series.

### `plot_multiple_runs`

**Status:** Experimental  
**Import:** `from abmforge import plot_multiple_runs`

Plot multiple run outputs.

### `plot_grid`

**Status:** Experimental  
**Import:** `from abmforge import plot_grid`

Plot a grid model state.

## Version API

### `__version__`

**Status:** Provisional  
**Import:** `from abmforge import __version__`

Current ABMForge package version.

## Full Public Export Checklist

The following names are exported from the root `abmforge` package and should
remain documented while they are part of `abmforge.__all__`:

- `Agent`
- `AgentCollection`
- `ContinuousSpace`
- `Recorder`
- `Dataset`
- `DATASET_SCHEMA_VERSION`
- `DatasetSchemaV1`
- `Event`
- `EventQueue`
- `Experiment`
- `ExperimentArchive`
- `ExperimentRegistry`
- `ExperimentResult`
- `GISSpace`
- `GridWorld`
- `Model`
- `NetworkSpace`
- `ODDDocument`
- `ParameterGrid`
- `RandomActivation`
- `ReplayValidationReport`
- `ReproducibilityManifest`
- `RunResult`
- `SALibProblem`
- `Scenario`
- `Scheduler`
- `SchemaValidationError`
- `SensitivityAnalysis`
- `SequentialActivation`
- `SimultaneousActivation`
- `StagedActivation`
- `__version__`
- `analyze_morris`
- `analyze_sobol`
- `attach_snapshot_hash`
- `link_snapshot`
- `plot_grid`
- `plot_multiple_runs`
- `plot_timeseries`
- `read_snapshot`
- `sample_morris`
- `sample_sobol`
- `snapshot_hash`
- `validate_replay`
- `write_snapshot`

## Internal APIs

The following should generally be treated as internal unless documented
elsewhere:

- underscore-prefixed modules, classes, functions, or variables;
- implementation helpers;
- test fixtures;
- private archive helpers;
- storage implementation details not listed in the public docs;
- experimental plugin prototypes.

## Documentation Contract

When a new symbol is added to `abmforge.__all__`, this page should be updated.
When a public symbol is removed or renamed, the API stability policy and
changelog should be updated as appropriate.
