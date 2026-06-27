# Mesa Comparison Benchmarks

This directory is reserved for future Mesa comparison work.

The current PR adds methodology only. It does not add Mesa as a dependency and
does not run Mesa benchmarks in CI.

## Intended Structure

Future comparison work may use:

```text
benchmarks/mesa/
  README.md
  methodology.md
  mesa_models/
  abmforge_models/
  scripts/
  results/
```

## Initial Candidate Models

Recommended first comparison cases:

- wealth inequality / money transfer;
- threshold diffusion;
- network diffusion;
- Schelling segregation;
- SIR epidemic.

## Rules

Do not add performance claims without:

- equivalent model code;
- repeated runs;
- raw results;
- environment metadata;
- version metadata;
- clear separation of runtime and output-writing time.

## CI Policy

Mesa comparison benchmarks should not become default CI gates until dependencies
are pinned, runtime is short, variance is understood, and thresholds are
justified.

For now, CI should only check that methodology documents exist.
