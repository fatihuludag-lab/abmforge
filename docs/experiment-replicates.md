# Experiment replicates

ABMForge supports repeated model runs through explicit seeds. The replicate
planning helper adds a small deterministic layer for designing repeated runs
before those runs are executed.

This page describes the planning utility only. It does not change
`Experiment.run()`, archive format, parallel execution, or scenario YAML
semantics.

## Why replicate planning matters

Agent-based models often need repeated runs for the same parameter
configuration because stochastic model dynamics can produce different outcomes
under different seeds.

A replicate plan makes this explicit:

- which parameter combination is being repeated,
- which replicate number is being run,
- which linear run index it has,
- which deterministic seed should be used.

## Basic usage

```python
from abmforge.experiment import SeedSequence, build_replicate_plan

plan = build_replicate_plan(
    parameter_count=3,
    replicates=5,
    seed_sequence=SeedSequence(base_seed=123),
)

for entry in plan:
    print(entry.to_dict())
```

Each entry contains:

```python
{
    "parameter_index": 0,
    "replicate_index": 0,
    "run_index": 0,
    "seed": 123456789,
}
```

The exact seed values depend on the `SeedSequence` configuration.

## Ordering

Replicate plans use parameter-major order:

```text
parameter_index=0, replicate_index=0
parameter_index=0, replicate_index=1
parameter_index=0, replicate_index=2
parameter_index=1, replicate_index=0
parameter_index=1, replicate_index=1
parameter_index=1, replicate_index=2
```

This order is stable and intended to match future experiment expansion logic.

## Start run index

Use `start_run_index` when appending planned runs after an existing sequence:

```python
from abmforge.experiment import SeedSequence, build_replicate_plan

plan = build_replicate_plan(
    parameter_count=2,
    replicates=3,
    seed_sequence=SeedSequence(base_seed=123),
    start_run_index=100,
)
```

The resulting entries will have run indexes `100..105`.

## Labels

Labels can separate seed streams for different experiment designs:

```python
from abmforge.experiment import SeedSequence, build_replicate_plan

baseline = build_replicate_plan(
    parameter_count=2,
    replicates=5,
    seed_sequence=SeedSequence(base_seed=123),
    label="baseline",
)

policy = build_replicate_plan(
    parameter_count=2,
    replicates=5,
    seed_sequence=SeedSequence(base_seed=123),
    label="policy",
)
```

The two plans are deterministic, but they produce different seed streams.

## Alpha-stage scope

This helper is intentionally small. It does not yet execute replicates. A future
experiment integration layer can use this plan to generate concrete `Scenario`
objects and attach replicate metadata to run records.
