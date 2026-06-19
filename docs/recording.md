# Recording Data

ABMForge records model-level metrics and agent-level variables through the model recorder.

The recorder writes structured records into the model dataset.

## Model-level metrics

Register a metric with `record.metric`.

```python
self.record.metric("mean_wealth", lambda model: model.agents.mean("wealth"))
```

The metric is collected after each model step by default.

## Recording frequency

Use `every` to record every N steps.

```python
self.record.metric(
    "mean_wealth",
    lambda model: model.agents.mean("wealth"),
    every=5,
)
```

This records the metric at steps divisible by 5.

## Conditional model recording

Use `when` to record only when a model-level condition is true.

```python
self.record.metric(
    "infected",
    lambda model: model.agents.sum("infected"),
    when=lambda model: model.steps >= 10,
)
```

## Agent-level variables

Register an agent variable with `record.agent`.

```python
self.record.agent("wealth")
```

This records the `wealth` attribute for agents that have that attribute.

## Agent recording frequency

```python
self.record.agent("wealth", every=10)
```

This records the variable every 10 model steps.

## Conditional agent recording

Use `when` to condition on model state.

```python
self.record.agent(
    "wealth",
    when=lambda model: model.steps >= 10,
)
```

Use `where` to select matching agents.

```python
self.record.agent(
    "wealth",
    where=lambda agent: agent.group == "treated",
)
```

You can combine `every`, `when`, and `where`.

```python
self.record.agent(
    "wealth",
    every=5,
    when=lambda model: model.steps >= 10,
    where=lambda agent: agent.group == "treated",
)
```

## Why this matters

Recording every variable at every step can create large datasets.

Frequency and conditional recording help users:

- reduce dataset size,
- focus on scientifically relevant moments,
- avoid unnecessary agent-level output,
- produce cleaner reproducible experiment archives.
