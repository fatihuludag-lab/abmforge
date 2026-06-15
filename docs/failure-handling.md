# Failure Handling

ABMForge treats failed runs as first-class experiment results.

This matters because parameter sweeps, seed replications, and long-running
computational experiments should not silently drop failed scenarios.

## Default behavior

By default, `Scenario.run()` re-raises exceptions:

```python
scenario.run()
```

This is useful during development because failures are visible immediately.

## Returning failed results

For batch experiments, a scenario can return a failed result instead of raising:

```python
result = scenario.run(raise_on_error=False)

assert result.status == "failed"
assert result.dataset.errors
```

## Experiments with `continue_on_error`

When `continue_on_error=True`, failed scenarios are included in the final
`ExperimentResult`:

```python
experiment = Experiment(
    scenarios=[scenario_a, scenario_b, scenario_c],
    continue_on_error=True,
)

result = experiment.run()

print(result.summary())
print(result.failed_count)
```

Failed runs can be inspected:

```python
for failed_run in result.failed():
    print(failed_run.run_id)
    print(failed_run.exception_type)
    print(failed_run.error)
    print(failed_run.dataset.errors)
```

## Error table

Each dataset has an `errors` table.

Error records include:

```text
error_id
run_id
step
time
component
exception_type
message
traceback
recoverable
event_id
agent_id
details
```

## Export

Dataset-level exports include errors:

```python
result.dataset.write_json("outputs/run")
result.dataset.write_csv("outputs/run")
```

Experiment-level CSV exports also include:

```text
errors.csv
```

## Research guidance

Do not ignore failed runs in published experiments.

Recommended reporting:

- number of scenarios,
- number of completed runs,
- number of failed runs,
- failure types,
- whether failures were excluded from analysis,
- whether failed runs were retried,
- software version and manifest hash.

Future versions of ABMForge will extend this with:

- failure artifacts,
- retry policies,
- resumable experiments,
- checkpoint-aware recovery.
