# Benchmarking

ABMForge benchmark support is currently a scaffold for repeatable measurement,
not a claim of superior performance.

The initial goal is to make future performance and comparison work:

- repeatable;
- low-cost to run locally;
- explicit about environment and configuration;
- suitable for CI smoke checks;
- honest about limitations.

## Scope

The benchmark scaffold focuses on:

- CLI scenario execution;
- experiment archive creation;
- archive validation;
- summary generation;
- installed-package behavior in later release checks.

It does not yet provide:

- statistically robust performance claims;
- large-scale simulations;
- distributed execution benchmarks;
- full Mesa/NetLogo/Agents.jl comparisons;
- memory profiling;
- regression thresholds.

Those should be added incrementally.

## Reference Suite

The reference benchmark entry point is:

```bash
python benchmarks/run_reference_suite.py
```

Useful commands:

```bash
python benchmarks/run_reference_suite.py --list
python benchmarks/run_reference_suite.py --quick
python benchmarks/run_reference_suite.py --quick --repeat 3 --output outputs/benchmarks/reference_suite.json
```

The benchmark runner writes JSON results with benchmark case name, command
sequence, repeat index, wall-clock duration, return code, Python version,
platform information, timestamp, and working directory.

## Interpreting Results

Benchmark results should be interpreted conservatively.

Wall-clock time can be affected by CPU model, power settings, operating system,
file system, antivirus scanning, Python version, dependency versions, cold vs
warm imports, and CI runner load.

Do not compare results across machines without recording the environment.

## Recommended Local Protocol

For local development:

1. run the quick benchmark once after major workflow changes;
2. run with `--repeat 3` before making performance claims;
3. save results under `outputs/benchmarks/`;
4. include Python and OS details in PR notes;
5. compare only against results from the same machine when possible.

Example:

```bash
python benchmarks/run_reference_suite.py --quick --repeat 3 --output outputs/benchmarks/pr_benchmark.json
```

## CI Usage

The benchmark scaffold is intentionally light.

CI should initially test that:

- the runner can list benchmark cases;
- benchmark docs exist;
- benchmark metadata fields are stable;
- benchmark output JSON schema remains readable.

Full timing comparisons should not gate CI until the project has a stable
performance baseline and variance policy.

## Future Benchmark Areas

Future benchmark work should include:

- API-level scenario run benchmark;
- CLI-level scenario run benchmark;
- multi-seed experiment benchmark;
- archive validation benchmark;
- CSV vs JSON vs Parquet output comparison;
- dataset query benchmark;
- model zoo benchmark cases;
- equivalent Mesa baseline models;
- benchmark result comparison utility;
- performance regression reporting.

## Reporting Benchmark Results

When reporting results, include:

- ABMForge version;
- commit hash;
- Python version;
- operating system;
- CPU model if available;
- command used;
- benchmark repeat count;
- whether the environment was warm or cold;
- output file path.

## Non-Goals

This benchmark scaffold does not claim that ABMForge is faster than other ABM
frameworks.

It is a foundation for careful, reproducible comparison work.
