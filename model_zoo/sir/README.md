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
|---|---|
| `width` | Width of the toroidal grid |
| `height` | Height of the toroidal grid |
| `n_agents` | Number of persons |
| `initial_infected` | Number of initially infected persons |
| `infection_prob` | Per-contact transmission probability |
| `recovery_prob` | Per-activation recovery probability |
| `steps` | Number of scenario or CLI execution steps |

## Update Semantics

The model uses asynchronous random activation.

An infected person can infect a susceptible neighbour by changing that
neighbour's state immediately. When the newly infected person is activated
later in the same scheduler pass, it may transmit infection during that same
pass.

The model is therefore an agent-based spatial SIR teaching model rather than
a discrete-time compartmental SIR difference equation.

## Scientific Verification

Executable checks are provided in
`tests/test_model_zoo_scientific_validation.py`.

Verified properties include:

- the population identity `S + I + R = N`;
- Susceptible counts do not increase;
- Recovered counts do not decrease;
- attack rate equals `(I + R) / N` and does not decrease;
- No initial infection is an absorbing state;
- `infection_prob = 0` prevents new cases;
- `recovery_prob = 0` prevents recovery;
- disease states remain within `S`, `I`, and `R`;
- same-seed trajectory reproducibility;
- recorded model metrics obey the same invariants.

## Interpretation Limits

The stochastic asynchronous model does not guarantee a single epidemic peak,
does not guarantee epidemic extinction within a fixed number of steps, and
does not imply empirical calibration.

Example epidemic curves are illustrative rather than fixed reference outputs.

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
