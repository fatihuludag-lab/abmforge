# Safe Experiment Recovery

ABMForge recovery determines which planned scenarios must run again when an
existing experiment archive is supplied. Recovery is deliberately
**fail-closed**: an archived run suppresses a planned run only when ABMForge can
validate a complete, versioned execution identity.

Recovery is not a general proof that two scientific executions are equivalent.
It is a conservative mechanism for avoiding reuse when the identity evidence is
missing, unsupported, or inconsistent.

## Identity layers

Three versioned structures participate in recovery:

- `run-index-v1` is the JSON container schema used by `run_index.json`.
- `run-identity-v2` defines the fields required for an archived run to be
  considered reusable.
- `execution-fingerprint-v1` provides an integrity-checked digest of the planned
  execution and its model source.

A completed run must satisfy all three contracts before it can match a planned
scenario.

## ExecutionFingerprintV1

`Scenario.execution_fingerprint()` creates an `ExecutionFingerprintV1` with:

- model class name;
- model module;
- model qualified name;
- model-source fingerprint kind;
- model-source SHA-256;
- scenario name;
- seed;
- requested step count;
- canonical parameter SHA-256;
- fingerprint schema version;
- canonical fingerprint digest.

The serialized fingerprint is stored in the dataset `runs` record and copied
into the corresponding `run_index.json` entry.

The provisional Python API is available from:

```python
from abmforge.repro import ExecutionFingerprintV1
```

Most users should obtain fingerprints through `Scenario` rather than construct
them directly:

```python
fingerprint = scenario.execution_fingerprint()
print(fingerprint.digest)
print(fingerprint.trusted)
```

## Model-source hashing

ABMForge uses the strongest locally available source representation in this
order:

1. SHA-256 of the complete Python module file (`module-file-sha256`).
2. SHA-256 of the inspected class source (`class-source-sha256`).
3. No source hash (`unavailable`).

A fingerprint with unavailable model source is untrusted and cannot suppress a
planned run. Hashing the complete module file is intentionally conservative: a
change elsewhere in the same module may cause the scenario to run again even
when the model class itself did not change.

## Matching rules

An archived entry is reusable only when all of the following are true:

1. The archived status is `completed`.
2. `run_identity_version` equals `run-identity-v2`.
3. An `execution_fingerprint` object is present.
4. Its schema is `execution-fingerprint-v1`.
5. Its required fields and digest pass integrity validation.
6. Model source is available, so the fingerprint is trusted.
7. The outer run-index metadata agrees with the fingerprint for model identity,
   scenario, seed, requested steps, and canonical parameters.
8. The planned scenario produces the same fingerprint digest.

Duplicate completed runs are counted, not collapsed. One archived run can
suppress only one equivalent planned scenario.

## Fail-closed behavior

ABMForge reruns the scenario when any relevant identity evidence is absent or
invalid. This includes:

- legacy `run-identity-v1` entries;
- missing fingerprints;
- unsupported fingerprint versions;
- modified or incomplete fingerprint payloads;
- disagreement between the fingerprint and outer run metadata;
- unavailable model source;
- changed model source;
- changed scenario name, seed, requested steps, or parameters;
- programmatic `stop_when` callbacks.

Programmatic stop conditions remain non-recoverable because arbitrary Python
callables do not yet have a persisted and stable identity contract.

## Legacy archive behavior

Older archives remain readable and valid for inspection. They are not silently
upgraded and are not automatically trusted for recovery.

To obtain reusable `run-identity-v2` records, execute the scenarios again with a
version of ABMForge that writes `execution-fingerprint-v1`. The new run metadata
and `run_index.json` entries will then carry the required identity evidence.

This policy prefers additional computation over silently reusing a scientifically
different run.

## Scope and limitations of v1

`execution-fingerprint-v1` currently covers model source, Python import identity,
scenario name, seed, requested steps, and parameters. It does **not** yet include:

- input dataset or external-file checksums;
- Git commit or dirty-tree state;
- dependency or interpreter versions;
- scheduler configuration beyond values represented by the model source and
  parameters;
- recorder configuration;
- plugin configuration or plugin source;
- arbitrary stop-condition callable identity.

Therefore a matching fingerprint is necessary, but not sufficient, evidence of
full scientific equivalence. Preserve source code, input data, environment
metadata, and the complete experiment archive for independent reconstruction.

Parameters should be JSON-compatible. Non-JSON objects are string-normalized in
the current alpha implementation and may not provide a portable identity across
processes or environments.
