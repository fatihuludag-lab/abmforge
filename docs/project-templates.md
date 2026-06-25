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
abmforge new segregation-study --template segregation
```

## Built-in templates

### `grid`

The `grid` template is a minimal grid-based ABM study. It includes a
wealth-transfer model on a `GridWorld`.

### `network`

The `network` template is a minimal network diffusion ABM study. It places
residents on a `NetworkSpace`; residents adopt through neighboring adopters or a
small broadcast probability.

### `epidemic`

The `epidemic` template is a minimal spatial SIR model on a `GridWorld`.
Individuals can be susceptible, infected, or recovered. Susceptible individuals
can become infected through nearby infected neighbors; infected individuals
recover with a configurable probability.

The generated experiment varies infection probability, recovery probability, and
contact radius. Its primary metric is `attack_rate`.

### `segregation`

The `segregation` template is a minimal Schelling-style spatial segregation
model on a `GridWorld`. Residents belong to one of two groups. They evaluate
local similarity, become unhappy below a homophily threshold, and relocate to
empty cells.

The generated experiment varies `homophily_threshold`. Its primary metric is
`mean_similarity`.

## Common workflow

Each template supports the same researcher workflow:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
abmforge report outputs/experiment
```

## Current scope

The template layer currently includes grid, network, epidemic, and segregation
starting points. Future templates may include policy and resource competition
starting points.
