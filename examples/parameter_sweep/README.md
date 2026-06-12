# Parameter Sweep Example

This example demonstrates how to run a parameter sweep with ABMForge.

It uses the Schelling segregation model and runs multiple combinations of density, homophily, and random seeds.

## Purpose

The goal is to show how ABMForge supports research-style computational experiments.

## ABM concepts

- Parameter sweep
- Repeated seeds
- Scenario generation
- Experiment result aggregation
- CSV export for downstream analysis

## How to run

Run this command from the repository root:

    python3 examples/parameter_sweep/run.py

## Experiment design

The example runs:

- 2 density values
- 3 homophily values
- 3 random seeds

Total runs:

    2 x 3 x 3 = 18 runs

## Output

The example writes CSV output to:

    outputs/parameter_sweep/

Generated files include:

- runs.csv
- model_records.csv
- agent_records.csv

## Key ABMForge APIs

- Experiment
- ParameterGrid
- ExperimentResult.summary
- ExperimentResult.write_csv
- Scenario
- Dataset
