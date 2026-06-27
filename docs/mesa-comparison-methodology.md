# Mesa Comparison Methodology

This document defines how ABMForge should be compared with Mesa.

It is a methodology document, not a performance claim.

## Why Compare with Mesa?

Mesa is one of the most visible Python frameworks for agent-based modelling.
It is a natural comparison point for ABMForge because both projects target
Python users building agent-based models.

ABMForge should not claim that it is a replacement for Mesa.

The comparison should instead clarify where ABMForge is trying to be different:

- reproducible scenario workflows;
- experiment-native execution;
- validated archive artifacts;
- dataset-first outputs;
- release-ready research project scaffolds;
- lightweight command-line research workflows;
- traceable model, scenario, and output bundles.

## Comparison Principles

A fair comparison should:

1. compare equivalent models;
2. use the same number of agents and steps;
3. use comparable random seeds;
4. report software versions;
5. report Python version and operating system;
6. separate runtime from output writing time;
7. separate model logic from framework overhead where possible;
8. avoid overstating performance differences;
9. include workflow and artifact quality, not just speed;
10. publish scripts and generated outputs.

## What Should Be Compared?

### Modelling API

Compare agent definition, model definition, scheduling or activation,
space/network support, model parameters, random seed handling, data collection,
and extensibility.

### Experiment Workflow

Compare scenario configuration, parameter sweeps, multi-seed experiments,
repeatability, CLI support, failure handling, run indexing, and output
organization.

### Research Artifacts

Compare whether each workflow produces explicit scenario or experiment config,
manifest or provenance metadata, dataset schema, run index, validation result,
analysis-ready tables, reproducibility guidance, and report outputs.

### Analysis Workflow

Compare ease of loading outputs, pandas compatibility, summary table generation,
robustness across seeds, sensitivity analysis support, and publication-ready
tables or figures.

### Packaging and Onboarding

Compare installation, template project creation, example model coverage,
documentation, release metadata, citation metadata, and community health files.

## What Should Not Be Claimed Yet?

Do not claim that ABMForge is:

- faster than Mesa;
- more scalable than Mesa;
- more mature than Mesa;
- a complete Mesa replacement;
- empirically validated for all domains;
- stable enough for all production ABM workloads.

Any future performance claim should be backed by benchmark code, raw results,
machine details, and repeated runs.

## Equivalent Model Selection

Start with small, transparent models:

1. wealth inequality / money transfer;
2. Schelling-style segregation;
3. SIR epidemic;
4. threshold diffusion;
5. network diffusion.

For each model, define agent count, step count, random seed policy, metrics
recorded, output format, run count, and expected qualitative behavior.

## Benchmark Dimensions

Future benchmarks may measure:

- model construction time;
- run time without output writing;
- run time with output writing;
- archive or output validation time;
- output directory size;
- memory use;
- time to load outputs for analysis;
- number of files produced;
- reproducibility metadata completeness.

Timing should use repeated runs and report summary statistics.

## Workflow Capability Matrix

A future comparison table should include:

| Capability | ABMForge | Mesa | Notes |
| --- | --- | --- | --- |
| Python-first ABM modelling | Yes | Yes | Both target Python users. |
| Scenario YAML workflow | Yes | To be evaluated | Compare documented workflows. |
| Multi-seed experiment abstraction | Yes | To be evaluated | Compare equivalent scripts. |
| Validated archive format | Yes | To be evaluated | Focus on artifact validation. |
| Dataset schema validation | Yes | To be evaluated | Compare output contracts. |
| Built-in model visualization | Limited | To be evaluated | Do not overclaim. |
| Model zoo maturity | Emerging | To be evaluated | Use current docs/releases. |

The Mesa column should be filled from current Mesa documentation and code, not
from memory.

## Reporting Template

Each benchmark or comparison report should include:

```text
ABMForge version:
Mesa version:
Python version:
Operating system:
CPU:
Memory:
Command:
Model:
Agent count:
Steps:
Seeds:
Output mode:
Archive validation:
Result files:
Timing summary:
Known limitations:
```

## Reproducibility Rules

Every comparison should preserve source code, model configuration, output
tables, archive or output directory, benchmark script, environment metadata,
raw timing results, and summary tables.

## Mesa-Specific Caution

Mesa has its own goals, user community, documentation, examples, and release
history. ABMForge comparisons should respect that maturity.

The intended ABMForge message is:

> ABMForge focuses on reproducible, experiment-native, archive-oriented ABM
> research workflows.

not:

> ABMForge is universally better than Mesa.

## Future Work

Recommended next PRs:

1. add a Mesa comparison benchmark directory;
2. implement one equivalent Mesa baseline model;
3. implement one equivalent ABMForge baseline model;
4. run local smoke comparisons;
5. record raw benchmark JSON;
6. add a feature/capability comparison table;
7. summarize findings in publication-oriented language.

## References for Manual Review

Before running or publishing comparisons, review current Mesa documentation,
the Mesa repository, and recent Mesa publication material. Do not rely on stale
memory for Mesa capabilities.
