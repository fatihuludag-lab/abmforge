# Archive Migration Strategy

ABMForge treats experiment archives as research artifacts.

This document defines the migration strategy for archive formats as ABMForge
moves from alpha toward beta and 1.0.

## Status

Current archive specification:

```text
experiment-archive-v1
```

Current status:

```text
alpha / provisional
```

The archive format is important because generated archives may be shared,
reviewed, cited, reproduced, or preserved alongside publications.

## Goals

Archive migration policy should:

- preserve research artifacts where practical;
- avoid silent data reinterpretation;
- make archive format versions explicit;
- fail clearly when an archive version is unsupported;
- provide migration guidance before format-breaking changes;
- keep old archives readable where reasonable;
- make any lossy migration explicit.

## Archive Version Fields

Archive readers should use explicit metadata before trying to infer structure.

Important version indicators include:

- `manifest.json`;
- archive format identifier;
- dataset schema version;
- run index schema;
- standard table names;
- standard field names.

For v1 archives, the expected archive format identifier is:

```text
experiment-archive-v1
```

## Compatibility Classes

ABMForge archive changes should be classified before merge.

### Compatible Additions

Compatible additions may include:

- new optional files;
- new optional report artifacts;
- new optional dataset tables;
- new optional manifest fields;
- new optional validation warnings;
- new optional metadata fields.

Compatible additions should not break existing archive readers.

### Soft-Breaking Changes

Soft-breaking changes may require documentation but can often be handled with
warnings or fallback behavior.

Examples:

- adding a new recommended field;
- changing report wording;
- changing non-essential report file names;
- adding validation warnings for previously tolerated issues.

### Breaking Changes

Breaking changes require explicit migration guidance.

Examples:

- renaming required files;
- changing required table names;
- changing required column names;
- changing semantics of standard fields;
- changing status values;
- changing dataset schema meaning;
- removing required metadata;
- changing archive validation error behavior in a way that affects scripts.

## Reader Behavior

Archive readers should follow this order:

1. locate the archive root;
2. read `manifest.json`;
3. determine archive format version;
4. determine dataset schema version;
5. check required files for that version;
6. validate required tables and fields;
7. report unsupported versions clearly.

Unsupported archive versions should raise or report a clear message such as:

```text
Unsupported archive format: experiment-archive-v2
```

The error should tell users what version is supported and where to find
migration guidance.

## Migration Principles

Archive migration should be:

- explicit;
- deterministic;
- logged;
- conservative;
- non-destructive by default;
- auditable.

A migration should not overwrite the original archive unless the user explicitly
requests it.

Preferred behavior:

```text
input archive -> migrated copy -> migration report
```

## Future CLI Design

A future migration command may look like:

```bash
abmforge archive migrate old_archive new_archive --to experiment-archive-v2
```

Possible options:

```bash
abmforge archive migrate old_archive new_archive --dry-run
abmforge archive migrate old_archive new_archive --to experiment-archive-v2
abmforge archive migrate old_archive new_archive --overwrite
abmforge archive migrate old_archive new_archive --report migration_report.json
```

This PR documents the strategy only. It does not implement the migration command.

## Migration Report

A migration report should include:

- source archive path;
- target archive path;
- source archive format;
- target archive format;
- source dataset schema version;
- target dataset schema version;
- files copied;
- files transformed;
- files skipped;
- warnings;
- errors;
- whether the migration was lossy;
- ABMForge version;
- timestamp.

## Lossy Migration

Lossy migration is discouraged.

If unavoidable, the migration report must state:

- what information was lost;
- why it could not be preserved;
- whether the original archive remains unchanged;
- how users can inspect the loss.

For published research artifacts, lossy migration should generally be avoided.

## Validation After Migration

After migration, users should run:

```bash
abmforge validate migrated_archive
abmforge summarize migrated_archive --json
```

If the archive was part of a published study, users should also compare:

- run count;
- scenario or experiment configuration;
- model records;
- agent records;
- error records;
- summary metrics;
- report outputs.

## Research Preservation Guidance

For published research, preserve the original archive even after migration.

Recommended preservation bundle:

- original archive;
- migrated archive;
- migration report;
- ABMForge version used for migration;
- source commit hash;
- dependency environment;
- publication or project identifier;
- notes explaining why migration was performed.

## Developer Checklist

Before changing archive format behavior, check:

- Does this change alter required files?
- Does this change alter required table names?
- Does this change alter required column names?
- Does this change alter field semantics?
- Does this change alter validation behavior?
- Does this change require a new archive format version?
- Does documentation need to be updated?
- Does a migration path need to be provided?
- Are old fixture archives still readable?
- Are archive validation tests updated?

## Current Non-Goals

This strategy does not yet implement:

- archive migration commands;
- automatic archive upgrades;
- long-term archive fixture matrix;
- binary compatibility guarantees;
- migration from third-party ABM frameworks;
- production archival storage;
- DOI or repository deposit workflows.

Those should be handled by later PRs.

## Roadmap

Recommended next steps:

1. add fixture archives for `experiment-archive-v1`;
2. add unsupported-version behavior tests;
3. add explicit archive format version reader;
4. design `abmforge archive migrate`;
5. implement dry-run migration report;
6. implement v1-to-v2 migration only when v2 exists;
7. add publication-preservation guidance to release docs.

## Summary

ABMForge should treat archives as durable research artifacts. Format evolution is
allowed during alpha, but changes should be explicit, documented, validated, and
migration-aware.
