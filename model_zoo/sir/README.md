# SIR Epidemic Model

This example demonstrates a classic Susceptible–Infected–Recovered (SIR) epidemic model implemented with ABMForge.

## Overview

The SIR model is one of the foundational models in epidemiology. Individuals transition through three states:

- Susceptible (S)
- Infected (I)
- Recovered (R)

Disease transmission emerges from interactions between agents, allowing users to study epidemic dynamics under different assumptions.

## Running the Example

```bash
python run.py
```

## Features

- Agent-based disease transmission
- State transitions (S → I → R)
- Random interactions
- Time-stepped simulation
- Dataset recording
- Reproducible experiments

## Model Parameters

| Parameter | Description |
|------------|-------------|
| population_size | Number of agents |
| initial_infected | Initially infected agents |
| infection_probability | Transmission probability |
| recovery_probability | Recovery probability |
| max_steps | Maximum simulation steps |

## Expected Behavior

Typical simulation dynamics:

1. A small number of agents start infected.
2. Infection spreads through contacts.
3. The infected population reaches a peak.
4. Recovery dominates.
5. The epidemic eventually ends.

## Example Output

```text
Step 0   : S=990 I=10 R=0
Step 20  : S=820 I=150 R=30
Step 40  : S=420 I=320 R=260
Step 60  : S=180 I=110 R=710
Step 100 : S=120 I=0 R=880
```

## Generated Datasets

The example can export:

- agent_state.csv
- model_state.csv
- event_log.csv

## Scientific Background

The SIR model was introduced by:

Kermack, W. O. and McKendrick, A. G. (1927)

A Contribution to the Mathematical Theory of Epidemics.

Proceedings of the Royal Society A.

## Learning Objectives

After studying this example, users should understand:

- Epidemic spreading mechanisms
- State-transition modeling
- Emergent population dynamics
- Data collection in ABMForge
- Reproducible simulation workflows

## Extensions

Possible extensions include:

- SEIR models
- Vaccination strategies
- Spatial diffusion
- Network-based transmission
- Policy intervention experiments

## Next Steps

After completing this example, consider exploring:

- Schelling Segregation Model
- Opinion Dynamics Model
- Market Simulation Model
- Network Diffusion Model
