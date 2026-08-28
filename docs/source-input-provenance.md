# Source and Input Provenance

ABMForge Manifest V1 can record two distinct forms of research provenance:

1. the source file and Git repository that define the executed model; and
2. external input files supplied explicitly by the researcher.

These records improve auditability, but they do not by themselves prove full
scientific equivalence between two executions.

## Model-source repository provenance

`ReproducibilityManifest.from_run_result()` derives Git provenance from the
executed model's defining source file. Repository discovery starts from that
file's directory and does **not** use `Path.cwd()` or the process current working directory.

```python
from abmforge import ReproducibilityManifest

manifest = ReproducibilityManifest.from_run_result(
    result,
    include_git=True,
    include_packages=False,
    include_command=False,
)

print(manifest.git)
```

A successful `source-repository-provenance-v1` record contains:

```json
{
  "schema_version": "source-repository-provenance-v1",
  "scope": "model-source",
  "source_available": true,
  "source_path": "models/market.py",
  "source_sha256": "...",
  "available": true,
  "commit": "...",
  "branch": "main",
  "dirty": false,
  "remote": "..."
}
```

`source_path` is repository-relative when a Git root is available. The source
file is always hashed with SHA-256 when it can be inspected, including when it
is not inside a Git repository.

When a model is created dynamically, defined in an interactive stream, or its
source cannot be inspected, ABMForge records a fail-closed value with
`source_available: false` instead of falling back to an unrelated repository.

### `from_run_result()` and `from_dataset()`

The model-source guarantee applies to `from_run_result()` because a
`RunResult` retains the executed model instance.

`ReproducibilityManifest.from_dataset()` does not necessarily have a model
object from which to discover the defining repository. Its optional Git record
continues to describe the caller's current working repository for backward
compatibility. Research workflows that require model-source provenance should
therefore build manifests from the `RunResult`.

## External input artifact provenance

Input files are opt-in. Pass each file explicitly and provide `input_root` when
portable study-relative paths are required:

```python
from pathlib import Path

from abmforge import ReproducibilityManifest

study_root = Path("study")
input_files = [
    study_root / "data" / "observations.csv",
    study_root / "config" / "policy.json",
]

manifest = ReproducibilityManifest.from_run_result(
    result,
    input_artifacts=input_files,
    input_root=study_root,
)
```

Each `input-artifact-v1` record contains:

```json
{
  "schema_version": "input-artifact-v1",
  "path": "data/observations.csv",
  "role": "input",
  "size_bytes": 1234,
  "sha256": "..."
}
```

The manifest also records `input_artifact_count`.

## Path and integrity rules

When `input_root` is supplied:

- the root must exist and be a directory;
- each input must resolve to a regular file;
- each resolved input must remain inside the resolved root;
- path traversal and symlink escape are rejected;
- paths are stored with portable POSIX separators;
- records are sorted by manifest path;
- duplicate manifest paths are rejected during validation.

The SHA-256 digest describes the raw bytes present when the manifest is
created. ABMForge does not automatically discover files opened by user model
code; every external input that matters to reconstruction must be supplied
explicitly.

## Inputs and generated artifacts are different

`input_artifacts` records external files consumed by the study. `artifacts`
records files generated or registered by the archive workflow. Keeping the two
inventories separate prevents archive finalization or report generation from
reclassifying research inputs as generated outputs.

## Current trust boundary

Source and input provenance strengthen auditability, but Manifest V1 does not
currently claim complete research reconstruction. In particular:

- input files are not discovered automatically;
- directory datasets require researchers to list their material files;
- `input-artifact-v1` checksums are not yet part of
  `execution-fingerprint-v2` recovery identity;
- Git commit metadata does not preserve an uncommitted patch;
- dependency and interpreter details remain separate manifest fields;
- external services, databases, environment variables, and secrets are not
  captured automatically.

A publication archive should preserve the manifest, all declared inputs, model
source, environment information, and the exact ABMForge release together.
