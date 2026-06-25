# Project templates

ABMForge project templates provide a researcher-friendly starting point for
new studies. They create a small project structure with configuration files,
model code, tests, and an output directory.

List available templates with:

```bash
abmforge templates
```

Machine-readable output is also available:

```bash
abmforge templates --json
```

Create a new study project with:

```bash
abmforge new my-study --template grid
abmforge new network-study --template network
abmforge new epidemic-study --template epidemic
```

## Built-in templates

### `grid`

The `grid` template is a minimal grid-based ABM study. It includes a
wealth-transfer model on a `GridWorld`.

Run the generated baseline with:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
```

Run the generated experiment with:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
abmforge report outputs/experiment
```

### `network`

The `network` template is a minimal network diffusion ABM study. It places
residents on a `NetworkSpace`; residents adopt through neighboring adopters or a
small broadcast probability.

Run the generated baseline with:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
```

Run the generated experiment and report with:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
abmforge report outputs/experiment
```

### `epidemic`

The `epidemic` template is a minimal spatial SIR model on a `GridWorld`.
Individuals can be susceptible, infected, or recovered. Susceptible individuals
can become infected through nearby infected neighbors; infected individuals
recover with a configurable probability.

The generated experiment varies infection probability, recovery probability, and
contact radius. Its primary metric is `attack_rate`.

Run the generated baseline with:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
```

Run the generated experiment and report with:

```bash
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
abmforge report outputs/experiment
```

## Current scope

The template layer currently includes grid, network, and epidemic starting
points. Future templates may include segregation, policy, and resource
competition starting points.
