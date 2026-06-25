# Reproducibility Tiers

ABMForge is a reproducibility-oriented alpha framework. This means the framework
provides tools that make experiments easier to seed, inspect, validate, archive,
and repeat. It does not yet guarantee full independent reproduction by default.

This page defines the current reproducibility tiers used by ABMForge.

## Why Tiers Are Needed

"Reproducibility" can mean different things:

- rerunning the same model with the same seed,
- obtaining the same scientific trajectory,
- producing the same normalized dataset,
- producing byte-identical serialized files,
- validating an archive after a run,
- or reconstructing a full experiment years later on another machine.

ABMForge separates these meanings because they require different technical
guarantees.

## Summary Table

| Tier | Name | Current Status | What It Means |
|---|---|---|---|
| Tier 0 | Installation and import reproducibility | Supported by CI and packaging checks | The package installs and public imports work |
| Tier 1 | Same-code seeded run reproducibility | Partially supported | Same code, same environment, same seed should produce the same model trajectory when user code is deterministic |
| Tier 2 | Normalized dataset reproducibility | Partially supported | Scientific records can match after ignoring expected volatile fields such as run IDs and timestamps |
| Tier 3 | Archive integrity reproducibility | Supported for current archive checks | Archive structure and supported dataset integrity checks pass |
| Tier 4 | Artifact byte reproducibility | Not guaranteed | Serialized files are byte-identical across runs and machines |
| Tier 5 | Independent reconstruction | Not yet supported by default | Source, inputs, dependencies, and environment are sufficient to reconstruct the experiment elsewhere |
| Tier 6 | Replay/checkpoint reproducibility | Experimental | Snapshot and replay behavior is limited and not a full checkpoint system |

## Tier 0: Installation and Import Reproducibility

Tier 0 asks whether ABMForge can be installed and imported consistently.

Examples:

```bash
python -m pip install -e ".[dev,data,viz,analysis,docs]"
python -m pip check
python -c "import abmforge; print(abmforge.__version__)"
```

ABMForge also tests public imports such as:

```python
from abmforge import Agent, Model, Scenario, Dataset, Recorder
```

This tier is necessary but not sufficient for scientific reproducibility.

## Tier 1: Same-Code Seeded Run Reproducibility

Tier 1 asks whether the same model code, same parameters, same dependency
environment, and same seed produce the same model trajectory.

ABMForge supports this through:

- model-level random number generation,
- explicit scenario seeds,
- deterministic scheduler behavior where applicable,
- deterministic `NetworkSpace` iteration order,
- and explicit parameter grids.

However, Tier 1 also depends on user model code. ABMForge cannot automatically
control all sources of nondeterminism, such as:

- Python's global `random` module,
- unordered external data structures,
- external libraries with their own random number generators,
- file system ordering,
- parallel execution,
- operating-system dependent behavior,
- or external services.

Recommended practice:

```python
model = MyModel(seed=42)
```

and avoid uncontrolled randomness inside model code.

## Tier 2: Normalized Dataset Reproducibility

Tier 2 asks whether scientifically meaningful records match across repeated runs
after expected volatile fields are ignored.

Examples of volatile fields:

- run IDs,
- timestamps,
- machine-specific paths,
- wall-clock durations,
- environment-specific metadata.

ABMForge datasets are structured into tables:

| Table | Purpose |
|---|---|
| `runs` | run-level metadata and status |
| `model_records` | model-level measurements |
| `agent_records` | agent-level measurements |
| `event_records` | event traces |
| `lifecycle_records` | agent lifecycle transitions |
| `errors` | structured failures |

Tier 2 is stronger than simply "the command ran". It means the scientific content
of the run can be compared in a structured way.

ABMForge does not yet define a universal normalized dataset comparator for every
model. Users should define expected invariants or comparison rules for their
own models.

## Tier 3: Archive Integrity Reproducibility

Tier 3 asks whether an archive is internally valid after a run.

A typical workflow is:

```bash
abmforge run examples/scenarios/wealth_baseline.yaml \
  --archive outputs/wealth_baseline_reference \
  --overwrite

abmforge validate outputs/wealth_baseline_reference
abmforge summarize outputs/wealth_baseline_reference --json
```

Archive validation currently checks supported archive and dataset integrity
properties, including:

- required archive structure,
- manifest readability,
- supported dataset table presence,
- JSON/JSONL dataset integrity,
- Parquet table presence,
- Parquet readability,
- Parquet row counts against manifest `record_counts`,
- and schema-related metadata checks where available.

Tier 3 means the archive is internally consistent according to current ABMForge
validators. It does not mean the archive contains everything required to rebuild
the experiment independently.

## Tier 4: Artifact Byte Reproducibility

Tier 4 asks whether serialized files are byte-identical across repeated runs.

ABMForge does not currently guarantee byte-identical artifacts.

Reasons include:

- run IDs,
- timestamps,
- JSON formatting choices,
- platform-dependent metadata,
- dependency versions,
- file ordering,
- compression behavior,
- and archive generation details.

Users should not currently expect byte-identical archives across machines or
runs unless they define and control all volatile fields themselves.

## Tier 5: Independent Reconstruction

Tier 5 asks whether someone else can reconstruct the experiment from preserved
materials.

An ABMForge archive alone is not yet a complete reconstruction bundle.

For independent reconstruction, preserve:

```text
model source code
scenario YAML files
input data files or content hashes
dependency lock files or environment exports
Python version
operating system information
ABMForge version or commit hash
analysis scripts
random seeds
configuration files
```

Recommended files:

```text
requirements.txt
requirements-lock.txt
environment.yml
pyproject.toml
uv.lock or poetry.lock, if used
Git commit hash
README explaining the exact run command
```

ABMForge may capture some metadata automatically, but users remain responsible
for preserving external source code, inputs, and environments.

## Tier 6: Replay and Checkpoint Reproducibility

Tier 6 asks whether an experiment can be checkpointed, restored, and continued
with equivalent behavior.

ABMForge currently has snapshot-related helpers, but full replay/checkpoint
reproducibility is experimental.

Current limitations include:

- not all world state is guaranteed to be restored,
- not all scheduler state is guaranteed to be restored,
- event queue restoration is not yet a complete replay system,
- custom model reconstruction requires explicit support,
- and snapshot semantics may change before a stable release.

Snapshot support should currently be treated as a useful inspection and
development feature, not a mature checkpoint/replay guarantee.

## Practical Recommendations

For local experiments:

1. Use explicit scenario files.
2. Use explicit seeds.
3. Write outputs to a clean archive path.
4. Run archive validation.
5. Save summaries.
6. Commit source code.
7. Preserve input data or hashes.
8. Preserve dependency information.

Example:

```bash
rm -rf outputs/wealth_baseline_reference

abmforge run examples/scenarios/wealth_baseline.yaml \
  --archive outputs/wealth_baseline_reference \
  --overwrite

abmforge validate outputs/wealth_baseline_reference
abmforge summarize outputs/wealth_baseline_reference --json
```

## Current ABMForge Claim

The safest current claim is:

> ABMForge is reproducibility-oriented alpha software.

This means ABMForge provides structured tools for seeded runs, dataset exports,
archive validation, and metadata capture, while still requiring users to preserve
source code, inputs, and environments for independent reproduction.

Avoid stronger claims such as:

- fully reconstruction-capable without additional artifacts,
- self-contained reconstruction by default,
- byte-identical archive reproduction,
- mature replay/checkpoint support,
- or production-grade reproducibility guarantees.

## Related Documentation

See also:

- `reference-reproducible-workflow.md`
- `reproducibility-manifest-v1.md`
- `experiment-archive.md`
- `dataset-schema-v1.md`
- `scenario-yaml.md`
