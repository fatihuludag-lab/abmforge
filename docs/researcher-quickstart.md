# Researcher Quickstart

This guide is for researchers who want to run ABMForge as a reproducible
agent-based modelling workflow.

The goal is to go from a clean checkout to a validated experiment archive and a
small report-oriented workflow.

Estimated time: 15 minutes.

## What You Will Do

You will:

1. install ABMForge for local development;
2. inspect the package and CLI;
3. run a documented scenario;
4. validate the generated experiment archive;
5. summarize the archive;
6. run the canonical reproducible study example;
7. identify the main files to cite or preserve for research use.

## Requirements

Use Python 3.10, 3.11, 3.12, or 3.13.

Check your Python version:

```bash
python --version
```

ABMForge is alpha-stage research software. For published work, pin the exact
version or commit and preserve the generated archive.

## Installation from Source

Clone the repository:

```bash
git clone https://github.com/fatihuludag-lab/abmforge.git
cd abmforge
```

Create and activate a virtual environment.

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install in editable mode with development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Check the installation:

```bash
abmforge --version
abmforge info
abmforge templates
```

## Installation from a Release

When a release is available from PyPI, users may install it with:

```bash
python -m pip install abmforge
```

For alpha-stage research artifacts, source checkout or pinned release versions
are preferred over unpinned installs.

## Start a Research Study from a Template

ABMForge includes a research-oriented project template:

```bash
abmforge new my-study --template research
cd my-study
```

Then run the generated workflow:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline_archive --overwrite
abmforge validate outputs/baseline_archive
abmforge summarize outputs/baseline_archive --json
abmforge experiment configs/experiment.yaml --archive outputs/experiment_archive --overwrite
python analysis/analyze.py outputs/experiment_archive
```

The template is intended to give researchers a reproducible starting structure with configuration files, model code, analysis code, and output directories.

## Run a Scenario

ABMForge ships a small documented scenario:

```bash
abmforge run examples/scenarios/wealth_baseline.yaml --archive outputs/wealth_baseline_archive --overwrite
```

Expected result:

- a completed run;
- a new archive directory under `outputs/wealth_baseline_archive`;
- run metadata;
- dataset tables;
- archive manifest;
- dataset schema;
- run index.

## Validate the Archive

Run:

```bash
abmforge validate outputs/wealth_baseline_archive
```

A valid archive should report no validation errors.

Archive validation is important because ABMForge treats generated experiment
outputs as research artifacts, not just temporary logs.

## Summarize the Archive

Run a human-readable summary:

```bash
abmforge summarize outputs/wealth_baseline_archive
```

Run a JSON summary:

```bash
abmforge summarize outputs/wealth_baseline_archive --json
```

The JSON output is useful for scripts, reports, and regression checks.

## Generate a Report

If the report command is available in your checkout, run:

```bash
abmforge report outputs/wealth_baseline_archive
```

The report output can be used as a starting point for model checking, project
notes, and research documentation.

## Run the Canonical Reproducible Study

The canonical study is under:

```text
examples/reproducible_study/
```

Run:

```bash
python examples/reproducible_study/reproduce.py
```

This workflow exercises:

- experiment configuration;
- multiple parameter combinations;
- multiple seeds;
- archive validation;
- summary generation;
- report generation;
- lightweight analysis outputs.

Expected outputs are written under the example output directory used by the
script.

## Load Archive Tables in Python

After validating an archive, you can load tables for custom analysis:

```python
from abmforge.analysis import load_archive_tables

tables = load_archive_tables("outputs/baseline_archive")
runs = tables["runs"]
model_records = tables["model_records"]
```

If pandas is installed, request DataFrames:

```python
tables = load_archive_tables("outputs/baseline_archive", as_dataframe=True)
```

## Summarize Robustness Across Runs

For multi-run archives, summarize final metrics by parameter values:

```python
from abmforge.analysis import summarize_metric_by_parameters, write_summary_csv

rows = summarize_metric_by_parameters(
    "outputs/experiment_archive",
    metric="adoption_share",
    group_by=["peer_influence"],
)
write_summary_csv(rows, "reports/robustness_summary.csv")
```

This produces descriptive statistics such as count, mean, standard deviation, minimum, and maximum for the selected metric.

## Files to Preserve for Research

For a reproducible ABMForge study, preserve:

- scenario or experiment YAML files;
- generated archive directory;
- `manifest.json`;
- `dataset_schema.json`;
- `run_index.json`;
- dataset tables under `data/`;
- report outputs;
- analysis scripts;
- source code commit hash;
- Python version and dependency environment.

For published research, also preserve input data and hashes where applicable.

## Minimal Python Workflow

ABMForge can also be used through Python.

```python
from abmforge import Agent, Model, Scenario


class Person(Agent):
    def step(self) -> None:
        self.wealth += 1


class WealthModel(Model):
    def setup(self) -> None:
        self.agents.create(Person, n=10, wealth=0)

    def step(self) -> None:
        self.agents.do("step")


scenario = Scenario(
    model=WealthModel,
    parameters={},
    seed=42,
    steps=5,
    name="quickstart",
)

result = scenario.run()

assert result.status == "completed"
```

For research workflows, prefer scenario or experiment YAML files when you want
auditable, reusable, and shareable configuration.

## Explore Research Model Zoo Examples

ABMForge includes executable research-oriented model zoo examples:

- `examples/model_zoo/wealth_inequality/`
- `examples/model_zoo/network_diffusion/`

Each example includes a baseline scenario, experiment configuration, analysis script, and expected output notes.

## Prepare a Publishable ABM Study

Before writing a manuscript, review the [ABM Study Checklist](abm-study-checklist.md). It covers model purpose, agents, environment, scheduling, parameters, seeds, archive validation, robustness summaries, calibration, validation, limitations, and code/data availability.

## Common Next Steps

After completing this guide:

- read the public API reference;
- read the API stability policy;
- inspect the experiment archive specification;
- run the reproducible study example;
- adapt an existing scenario YAML;
- create a small model-specific archive;
- use the benchmark scaffold only for conservative local measurement.

## Troubleshooting

### `abmforge` command not found

Use the virtual environment Python directly:

```bash
python -m abmforge.cli.main --version
```

Then confirm your environment is active.

### Scenario import error

Make sure you run commands from the repository root unless the scenario file
uses absolute import paths.

### Archive already exists

Use `--overwrite` only when it is safe to delete the previous archive:

```bash
abmforge run examples/scenarios/wealth_baseline.yaml --archive outputs/wealth_baseline_archive --overwrite
```

### Validation fails

Inspect the validation error message first. Common causes include:

- incomplete run output;
- manually edited archive files;
- missing dataset tables;
- schema mismatch;
- incompatible archive format.

## Research Caution

ABMForge helps structure simulations and outputs, but scientific validity still
depends on:

- model assumptions;
- calibration;
- sensitivity analysis;
- validation against domain evidence;
- transparent reporting;
- careful interpretation.

Do not treat a valid archive as evidence that the model itself is scientifically valid.
