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

## Fail-fast experiments and partial results

The default experiment policy is `continue_on_error=False`. Execution stops
after the first failed run and raises `ExperimentExecutionError`.

```python
from abmforge import ExperimentExecutionError

try:
    result = experiment.run()
except ExperimentExecutionError as exc:
    partial_result = exc.result
    failed_run = exc.failed_result
    original_error = exc.__cause__
```

The partial `ExperimentResult` contains:

- every completed run reached before the failure;
- the failed `RunResult`;
- its dataset and non-recoverable error record.

Scenarios that were not reached are not added to the partial result.

The failed run remains auditable:

```python
assert failed_run.status == "failed"
assert failed_run.dataset.errors[-1]["recoverable"] is False
```

## Experiment CLI exit contract

Without `--continue-on-error`, `abmforge experiment` stops after the first
failed run, writes a valid partial archive, and exits with status code `1`.

With `--continue-on-error`, all planned runs are attempted. The complete
archive is written, including failed runs. The command still exits with status
code `1` when one or more runs failed; continuing execution does not convert
failure into CLI success.

A fully successful experiment exits with status code `0`.

`reports/experiment_summary.json` records:

- `execution_status`;
- `run_count_expected`;
- `run_count_executed`;
- `unexecuted_count`;
- the normal `result_summary`.

The possible execution statuses are:

| Status | Meaning |
|---|---|
| `completed` | All planned runs executed and none failed |
| `completed_with_failures` | All planned runs executed, but at least one failed |
| `partial` | Execution stopped before all planned runs were attempted |

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

ABMForge researcher reports preserve failed and other non-completed runs in
status and failure tables, but exclude their partial metric observations from
metric summaries, parameter-effect estimates, and primary-metric rankings.
Only runs whose status is exactly `completed` contribute to these analytical
tables.

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
