# Model Zoo

ABMForge includes a growing collection of reference models that demonstrate common agent-based modeling patterns, scientific workflows, and best practices.

## Purpose

The Model Zoo serves three purposes:

1. Learning ABMForge
2. Providing reproducible scientific examples
3. Offering reusable starting points for research projects

## Available Models

### Schelling Segregation

Location:

model_zoo/schelling/

Demonstrates:
- Grid environments
- Agent relocation
- Neighborhood analysis
- Emergent segregation

### SIR Epidemic

Location:

model_zoo/sir/

Demonstrates:
- Disease transmission
- State transitions
- Population dynamics
- Epidemiological simulation

## Scientific verification contract

The canonical Schelling and SIR models have executable scientific verification
in `tests/test_model_zoo_scientific_validation.py`.

The suite covers:

- conservation and state-transition invariants;
- deterministic boundary conditions;
- model-specific metamorphic relations;
- same-seed trajectory reproducibility;
- consistency between recorded metrics and model state.

This evidence verifies internal model logic against the documented model
contract. It does not constitute empirical validation or calibration against
observed social or epidemiological data.

### SIR verified properties

The SIR model uses asynchronous random activation. A newly infected person may
therefore be activated later in the same scheduler pass and transmit infection
again during that pass.

Verified properties include:

- `S + I + R = N`;
- susceptible counts do not increase;
- recovered counts do not decrease;
- attack rate equals `(I + R) / N` and does not decrease;
- no initial infection is an absorbing state;
- zero infection probability prevents new cases;
- zero recovery probability prevents recovery;
- infection probability is irrelevant when every person is already infected;
- same-seed trajectory reproducibility;
- recorded epidemic metrics satisfy the same invariants.

These tests do not require infected counts to be monotone, do not require a
single epidemic peak, and do not require every finite run to end with zero
infected agents.

### Schelling verified properties

Verified properties include:

- population, group membership, and vacancy conservation;
- unique single-cell occupancy;
- valid ranges for mean similarity and unhappy-household counts;
- zero-density, single-group, and zero-homophily boundary behavior;
- group-label swap symmetry;
- a non-decreasing unhappy-household count as homophily increases on a fixed
  spatial configuration;
- same-seed trajectory reproducibility;
- synchronization of the recorded `happy` state with the final post-step
  spatial configuration;
- consistency of recorded population, vacancy, similarity, and unhappiness
  metrics.

The tests do not claim that higher homophily produces greater segregation in
every stochastic run. Such a claim would require an explicitly designed
multi-seed statistical experiment and a declared segregation measure.

This verification does not claim that higher homophily produces greater
segregation in every stochastic run.

## Planned Models

### Opinion Dynamics
- Consensus formation
- Polarization
- Social influence

### Wealth Distribution
- Economic inequality
- Wealth exchange
- Redistribution

### Market Simulation
- Financial markets
- Trading agents
- Market microstructure

### Predator-Prey
- Ecological systems
- Population cycles

### Flocking
- Collective motion
- Self-organization

### Network Diffusion
- Information spreading
- Cascade dynamics

## Common Structure

Each model follows:

model_name/
├── README.md
├── model.py
├── agents.py
├── run.py
└── config.py

## Reproducibility

Every example should:

- Support deterministic seeds
- Export datasets
- Document parameters
- Include scientific references

## Dataset Outputs

Examples may export:

- agent_state.csv
- model_state.csv
- event_log.csv

## Educational Goals

The Model Zoo helps users:

- Learn ABM concepts
- Learn ABMForge APIs
- Build research-grade simulations
- Develop reproducible workflows

## Roadmap

Near-term additions:

- Opinion Dynamics
- Wealth Distribution
- Market Simulation

Long-term additions:

- Reinforcement Learning Agents
- Multi-layer Networks
- Spatial Economics
- Large-scale Simulation Benchmarks
