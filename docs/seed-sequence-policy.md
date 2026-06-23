# Seed Sequence Policy

ABMForge provides a small deterministic seed derivation helper for experiment workflows.

The goal is to make seed assignment explicit and inspectable before adding higher-level replicate and batch experiment features.

This helper does not change existing `Scenario` or `Experiment` execution behaviour. It is a standalone utility that future experiment-management features can build on.

## Why this exists

Agent-based modelling studies often need repeated runs across:

- multiple scenarios;
- multiple parameter combinations;
- multiple replicates;
- multiple random seeds.

A clear seed policy helps researchers answer questions such as:

- Which seed was used for a run?
- Can the same seed sequence be regenerated from a base seed?
- How are parameter and replicate indices mapped to seeds?
- Are generated seeds stable across Python processes?

ABMForge uses a stable SHA-256 based derivation scheme rather than Python's built-in `hash()` function. Python's built-in hash may vary across processes, so it should not be used for persistent experiment seed derivation.

## Basic usage

```python
from abmforge.experiment import SeedSequence

seeds = SeedSequence(base_seed=123).generate(5)
```

`generate()` returns a deterministic list of unique integer seeds.

## Deriving seeds for parameter and replicate indices

```python
from abmforge.experiment import SeedSequence

sequence = SeedSequence(base_seed=123)

seed = sequence.derive(
    parameter_index=2,
    replicate_index=4,
)
```

This pattern is intended for future experiment workflows where each parameter combination may be repeated with multiple replicates.

## Labels

A label can be used to separate seed streams:

```python
from abmforge.experiment import SeedSequence

sequence = SeedSequence(base_seed=123)

baseline_seeds = sequence.generate(10, label="baseline")
policy_seeds = sequence.generate(10, label="policy")
```

Changing the label changes the generated stream while keeping the process deterministic.

## Seed range

By default, seeds are generated in the range:

```text
0 <= seed <= 2**32 - 1
```

This range is convenient for common random number generator APIs.

A smaller range can be configured for testing:

```python
from abmforge.experiment import SeedSequence

seeds = SeedSequence(base_seed=123, max_seed=9).generate(10)
```

## Current alpha boundary

This feature is a deterministic seed derivation utility. It is not yet a full experiment replicate manager.

In particular, this page does not claim that ABMForge currently provides:

- automatic replicate execution;
- mature distributed experiment scheduling;
- complete replay or checkpoint reconstruction;
- full environment reconstruction.

Those features require additional workflow and archive support.
