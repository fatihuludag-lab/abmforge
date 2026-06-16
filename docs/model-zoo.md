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
