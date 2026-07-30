# Schelling Segregation Model

This example demonstrates a classic Schelling Segregation Model implemented with ABMForge.

## Overview

The Schelling model is one of the most influential agent-based models in the social sciences. It illustrates how mild individual preferences can produce strong segregation patterns at the population level.

Agents belong to different groups and evaluate the composition of their local neighborhood. If an agent is dissatisfied, it relocates to a new position.

## Running the Example

```bash
python run.py
```

## Features

- Agent creation
- Grid-based environments
- Neighborhood queries
- Agent movement
- Emergent behavior
- Dataset recording
- Reproducible experiments

## Learning Objectives

- Understand local interactions
- Observe emergence
- Learn ABMForge grid spaces
- Collect simulation outputs
- Analyze segregation dynamics

## Model Parameters

| Parameter | Description |
|---|---|
| `width` | Width of the toroidal grid |
| `height` | Height of the toroidal grid |
| `density` | Share of grid cells initially occupied |
| `homophily` | Minimum same-group neighbour share required for happiness |
| `steps` | Number of scenario or CLI execution steps |

## Scientific Verification

Executable checks are provided in
`tests/test_model_zoo_scientific_validation.py`.

Verified properties include:

- population and vacancy counts are conserved;
- household identities and group counts are conserved;
- each occupied cell contains at most one household;
- population plus vacancies equals total grid capacity;
- mean similarity remains within `[0, 1]`;
- unhappy-household counts remain within valid population bounds;
- zero-density, single-group, and zero-homophily boundary behavior;
- group-label swap symmetry;
- unhappy-household count is non-decreasing as homophily increases on a fixed
  spatial configuration;
- same-seed trajectory reproducibility;
- `happy` is synchronized with the final post-step spatial state;
- recorded model metrics satisfy the same invariants.

## Interpretation Limits

The verification checks model logic and derived-state consistency. It is not
empirical validation of residential segregation.

The suite does not claim that higher homophily produces greater segregation in
every stochastic run. Such a relationship requires a multi-seed experiment,
an explicit segregation statistic, and statistical uncertainty reporting.
