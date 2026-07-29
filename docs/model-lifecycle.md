# Model Lifecycle

> **Normative semantics:** Model status transitions are documented here. The
> authoritative execution-phase order, stop-condition timing, partial-step
> failure behavior, and analysis-status distinction are defined in
> [Simulation Semantics V1](simulation-semantics-v1.md).

ABMForge models have an explicit execution lifecycle.

The lifecycle contract keeps model state, execution flags, scenario results,
and failure handling consistent and auditable.

## Lifecycle statuses

ABMForge defines five model statuses:

| Status | Meaning |
|---|---|
| `created` | The model exists but has not started executing |
| `running` | The model is actively executing simulation steps |
| `completed` | The requested execution finished normally |
| `stopped` | Execution ended intentionally before normal completion |
| `failed` | Execution ended because an exception occurred |

A newly constructed model starts with:

```python
model.status == "created"
model.running is False
```

## Normal execution

Calling `Model.run_for(...)` moves an eligible model into the running state:

```text
created
  -> running
  -> completed
```

After normal completion:

```python
model.status == "completed"
model.running is False
```

This also applies to zero-step runs:

```python
model.run_for(0)

assert model.status == "completed"
assert model.running is False
```

## Continuing a completed model

A completed model may be advanced again through an explicit `run_for(...)`
call:

```text
completed
  -> running
  -> completed
```

Example:

```python
model.run_for(5)
model.run_for(10)

assert model.steps == 15
assert model.status == "completed"
assert model.running is False
```

This supports controlled continuation workflows, including continuation after
a snapshot has been restored.

## Intentional stopping

Calling `model.stop(...)` ends the current execution intentionally:

```text
created or running
  -> stopped
```

A stopped model has:

```python
model.status == "stopped"
model.running is False
```

The optional reason is available through:

```python
model.stop_reason
```

Scenarios also use the stopped state when a `stop_when` callback returns
`True`. In that case, the run result records:

```python
result.status == "stopped"
result.stop_reason == "stop_condition"
```

## Failure handling

If model execution raises an exception, the model moves to the failed state
before the exception is propagated or captured by a scenario:

```text
created or running
  -> failed
```

After failure:

```python
model.status == "failed"
model.running is False
```

The completed step count includes only steps that finished successfully.
A step that raises before completion does not increment `model.steps`.

Scenario failures follow the same invariant:

```python
result.status == "failed"
result.model.status == "failed"
result.model.running is False
```

This applies to failures during setup, stepping, event processing, recording,
and stop-condition evaluation.

## Restart restrictions

`stopped` and `failed` are terminal states for a model instance.

Calling `run_for(...)` on either state raises `RuntimeError` and leaves the
model unchanged:

```python
model.stop("manual")

model.run_for(1)  # raises RuntimeError
```

A failed model is not silently retried because its internal state may be
partially updated and no longer scientifically trustworthy.

To perform another run after stopping or failure, construct a new model
instance or restore a separately validated snapshot.

## Scenario execution

During a multi-step `Scenario.run()`, the model remains in the running state
between individual steps:

```python
model.status == "running"
model.running is True
```

The model does not temporarily become `completed` after each intermediate
step.

At the end of scenario execution, exactly one terminal state is recorded:

| Outcome | Model status | `running` |
|---|---|---|
| Requested steps completed | `completed` | `False` |
| Model or stop condition stopped execution | `stopped` | `False` |
| Execution raised an exception | `failed` | `False` |

## State transition summary

```text
created   -> running -> completed
completed -> running -> completed

created   -> stopped
running   -> stopped

created   -> failed
running   -> failed

stopped   -X-> running
failed    -X-> running
```

`-X->` denotes a rejected transition.

## Research reproducibility recommendation

When model stopping or continuation is part of the scientific design,
document:

- the requested number of steps;
- the actual completed number of steps;
- all stop conditions;
- the recorded stop reason;
- whether continuation from a completed state is permitted by the study
  design;
- how failed runs are excluded, repeated, or replaced.

This makes early termination, continuation, and failure treatment transparent
when results are reproduced or audited.
