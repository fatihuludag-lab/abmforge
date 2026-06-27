# ABM Study Checklist and Reporting Guide

This guide helps researchers use ABMForge to prepare transparent,
reproducible, and reviewable agent-based modelling studies.

It is a checklist, not a guarantee of scientific validity.

A valid ABMForge archive means that the output artifact is structurally
checkable. Scientific credibility still depends on model assumptions,
calibration, validation, sensitivity analysis, and domain interpretation.

## How to Use This Checklist

Use this checklist when:

- starting a new ABM study;
- preparing a reproducible archive;
- writing a manuscript;
- preparing supplementary materials;
- reviewing a model before submission;
- teaching ABM research workflows.

Recommended workflow:

```bash
abmforge new my-study --template research
cd my-study
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge validate outputs/baseline_archive
abmforge summarize outputs/baseline_archive --json
```

For multi-run experiments:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment_archive --overwrite
abmforge validate outputs/experiment_archive
abmforge summarize outputs/experiment_archive --json
```

## 1. Research Question and Scope

Before writing model code, document:

- [ ] Model purpose.
- [ ] Research question.
- [ ] Target phenomenon.
- [ ] Unit of analysis.
- [ ] Spatial scope.
- [ ] Temporal scope.
- [ ] Intended audience.
- [ ] What the model is not intended to explain.
- [ ] Expected qualitative behavior or stylized facts.
- [ ] Main outcome variables.

Reporting guidance:

> State the model's purpose before describing implementation details. A reader
> should understand what the model is for and what it deliberately omits.

## 2. Agents

Document all agent types.

For each agent type, report:

- [ ] Agent class name.
- [ ] Agent role.
- [ ] State variables.
- [ ] Decision rules.
- [ ] Behavioral assumptions.
- [ ] Heterogeneity.
- [ ] Initialization.
- [ ] Birth, death, entry, or exit rules.
- [ ] Interactions with other agents.
- [ ] Random components.

Reporting guidance:

> Describe agent behavior in domain language first, then map it to code and
> parameters.

## 3. Environment and Space

Document the environment in which agents interact.

Checklist:

- [ ] Environment type.
- [ ] Grid, network, continuous, GIS, or abstract space.
- [ ] Boundary conditions.
- [ ] Neighborhood definition.
- [ ] Distance or adjacency rules.
- [ ] Exogenous resources or shocks.
- [ ] Environmental state variables.
- [ ] Whether the environment changes over time.

ABMForge examples may use `GridWorld`, `NetworkSpace`, `ContinuousSpace`, or
custom model logic.

## 4. Time, Scheduling, and Events

Document time semantics.

Checklist:

- [ ] Time unit.
- [ ] Number of steps.
- [ ] Scheduler or activation mechanism.
- [ ] Sequential, random, simultaneous, or staged activation.
- [ ] Event queue use, if any.
- [ ] Whether actions happen synchronously or asynchronously.
- [ ] How ties or simultaneous decisions are handled.
- [ ] Whether scheduling affects results.

Reporting guidance:

> Scheduling can change ABM outcomes. Treat it as a modelling assumption, not a
> technical detail.

## 5. Parameters and Initial Conditions

Provide a parameter table.

Minimum fields:

| Parameter | Meaning | Type | Baseline | Range | Source or rationale |
| --- | --- | --- | --- | --- | --- |

Checklist:

- [ ] All parameters are listed.
- [ ] Baseline values are reported.
- [ ] Experiment ranges are reported.
- [ ] Initial conditions are documented.
- [ ] Parameter units are given where relevant.
- [ ] Parameter choices are justified.
- [ ] Fixed and varied parameters are separated.
- [ ] Values in the manuscript match scenario or experiment YAML.

ABMForge guidance:

- Put baseline settings in `configs/baseline.yaml`.
- Put parameter sweeps in `configs/experiment.yaml`.
- Preserve both files with the archive.

## 6. Randomness and Seeds

Document all random processes.

Checklist:

- [ ] Random seed policy.
- [ ] Number of seeds.
- [ ] Master seed, if used.
- [ ] Per-run seed generation rule.
- [ ] Stochastic components.
- [ ] Whether same-seed reproducibility was checked.
- [ ] Whether results are robust across seeds.

Reporting guidance:

> A single seed is usually insufficient for stochastic ABM evidence. Report
> seed variation and robustness summaries where possible.

## 7. Scenario and Experiment Design

For each scenario or experiment, document:

- [ ] Scenario name.
- [ ] Model class.
- [ ] Baseline parameters.
- [ ] Number of steps.
- [ ] Stop conditions.
- [ ] Parameter grid.
- [ ] Seed count.
- [ ] Primary metric.
- [ ] Expected output archive path.

ABMForge commands:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge experiment configs/experiment.yaml --archive outputs/experiment_archive --overwrite
```

## 8. Output Data and Archive

A research-ready ABMForge study should preserve the generated archive.

Preserve:

- [ ] `manifest.json`
- [ ] `dataset_schema.json`
- [ ] `run_index.json`
- [ ] `configs/`
- [ ] `data/runs.*`
- [ ] `data/model_records.*`
- [ ] `data/agent_records.*`, if used
- [ ] `data/event_records.*`, if used
- [ ] `data/errors.*`, if present
- [ ] `reports/`
- [ ] analysis scripts
- [ ] environment metadata
- [ ] source commit hash

Validate:

```bash
abmforge validate outputs/experiment_archive
```

Reporting guidance:

> State whether archive validation passed and preserve the archive with the
> manuscript's supplementary materials or repository.

## 9. Analysis and Robustness

Use archive table helpers for custom analysis:

```python
from abmforge.analysis import load_archive_tables

tables = load_archive_tables("outputs/experiment_archive")
model_records = tables["model_records"]
```

Use robustness helpers for grouped summaries:

```python
from abmforge.analysis import summarize_metric_by_parameters, write_summary_csv

rows = summarize_metric_by_parameters(
    "outputs/experiment_archive",
    metric="adoption_share",
    group_by=["peer_influence"],
)

write_summary_csv(rows, "reports/robustness_summary.csv")
```

Checklist:

- [ ] Primary outcome metric is defined.
- [ ] Final-step and time-series metrics are distinguished.
- [ ] Seed variability is reported.
- [ ] Parameter variability is reported.
- [ ] Robustness summary table is generated.
- [ ] Sensitivity analysis is described.
- [ ] Figures and tables are generated from archived data.
- [ ] Analysis scripts are preserved.

## 10. Calibration and Validation

Separate calibration from validation.

Calibration asks:

> How were model parameters chosen or estimated?

Validation asks:

> Does the model reproduce relevant observed patterns or stylized facts?

Checklist:

- [ ] Calibration target is defined, if any.
- [ ] Validation target is defined, if any.
- [ ] Observed data source is described, if used.
- [ ] Stylized facts are listed, if used.
- [ ] Goodness-of-fit or distance metric is reported, if used.
- [ ] Out-of-sample or holdout logic is described, if applicable.
- [ ] Limitations of validation evidence are stated.

Reporting guidance:

> Do not treat successful execution or archive validation as model validation.

## 11. ODD and Model Documentation

ABM studies should be understandable outside the codebase.

Checklist:

- [ ] ODD document is prepared or exported.
- [ ] Purpose is stated.
- [ ] Entities, state variables, and scales are described.
- [ ] Process overview is described.
- [ ] Scheduling is described.
- [ ] Design concepts are described.
- [ ] Initialization is described.
- [ ] Input data is described.
- [ ] Submodels are described.
- [ ] Model limitations are stated.

ABMForge can help generate ODD-style skeletons, but scientific review and
manual editing are still required.

## 12. Reproducibility Package

A reproducibility package should include:

- [ ] Source code.
- [ ] ABMForge version.
- [ ] Python version.
- [ ] Dependency lock file or environment description.
- [ ] Scenario and experiment YAML files.
- [ ] Archive outputs.
- [ ] Validation logs.
- [ ] Analysis scripts.
- [ ] Figures and tables.
- [ ] README with reproduction commands.
- [ ] License.
- [ ] Citation metadata.
- [ ] DOI or repository link when available.

Recommended command summary:

```bash
abmforge info
abmforge validate outputs/experiment_archive
abmforge summarize outputs/experiment_archive --json
```

## 13. Manuscript Reporting Checklist

A manuscript should report:

- [ ] Model purpose.
- [ ] Agent types.
- [ ] Environment.
- [ ] Decision rules.
- [ ] Scheduling.
- [ ] Parameters.
- [ ] Initial conditions.
- [ ] Random seed policy.
- [ ] Experiment design.
- [ ] Number of runs.
- [ ] Outcome metrics.
- [ ] Sensitivity or robustness checks.
- [ ] Calibration approach.
- [ ] Validation evidence.
- [ ] Limitations.
- [ ] Code availability.
- [ ] Data availability.
- [ ] Archive availability.
- [ ] Software citation.

## 14. Code and Data Availability

Report:

- repository URL;
- release tag or commit hash;
- ABMForge version;
- input data availability;
- generated archive availability;
- analysis scripts;
- license;
- citation instructions.

Example wording:

```text
The ABMForge experiment archive, scenario configuration, experiment
configuration, and analysis scripts are available in the accompanying repository.
The archive was validated using `abmforge validate`.
```

## 15. Reviewer-Facing Quick Check

Before submission, verify:

- [ ] A new user can install the software.
- [ ] A new user can run the baseline scenario.
- [ ] A new user can validate the archive.
- [ ] A new user can reproduce the main table.
- [ ] A new user can reproduce the main figure.
- [ ] The paper's parameter values match the configuration files.
- [ ] The reported number of runs matches `run_index.json`.
- [ ] The code and data availability statement is accurate.

## Current Limitations

This guide does not yet provide:

- domain-specific validation standards;
- automatic calibration workflows;
- automatic manuscript generation;
- full ODD completeness checking;
- statistical inference guarantees;
- peer-review acceptance guarantees.

It is intended to make ABM research workflows more transparent, not to replace
scientific judgment.
