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
abmforge new policy-study --template policy
abmforge new resource-study --template resource
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

### `segregation`

The `segregation` template is a minimal Schelling-style spatial segregation
model on a `GridWorld`. Residents belong to one of two groups. They evaluate
local similarity, become unhappy below a homophily threshold, and relocate to
empty cells.

### `policy`

The `policy` template is a minimal intervention study on a `GridWorld`.
Residents differ in risk level. A policy assigns an intervention either randomly
or by risk priority. Treated residents may comply with the intervention, which
reduces accumulated outcome burden.

### `resource`

The `resource` template is a minimal renewable resource competition model on a
`GridWorld`. Foragers move toward nearby high-resource cells, harvest renewable
resources, pay a metabolism cost, and accumulate wealth.

The generated experiment varies resource regrowth, metabolism, and harvest rate.
Its primary metric is `mean_wealth`.

## Common workflow

Each template supports the same researcher workflow:

```bash
abmforge run configs/baseline.yaml --archive outputs/baseline --overwrite
abmforge experiment configs/experiment.yaml --archive outputs/experiment --overwrite
abmforge report outputs/experiment
```

## Current scope

The template layer currently includes grid, network, epidemic, segregation,
policy, and resource starting points.
