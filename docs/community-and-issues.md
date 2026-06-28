# Community and Issue Reporting

ABMForge is alpha-stage scientific software. High-quality issue reports help
keep the framework reliable, reproducible, and useful for research and teaching.

## Where to report

Use GitHub Issues for:

- reproducible bugs;
- documentation problems;
- feature requests;
- scenario, archive, manifest, or validation issues;
- reproducibility reports.

Use GitHub Discussions for open-ended questions, modeling ideas, and teaching
support when Discussions are enabled.

Security issues should follow `SECURITY.md`.

## Issue templates

ABMForge provides three main issue templates:

- bug report;
- feature request;
- reproducibility report.

The reproducibility report is intended for problems involving scenario files,
experiment archives, manifests, checksums, deterministic seeds, ODD artifacts, or
reproduced outputs.

## Repository settings note

For a public alpha release, GitHub issue creation should be enabled unless there
is a deliberate support policy explaining why it is restricted. If issue creation
is restricted, `SUPPORT.md` should state the alternative reporting channel.

## Good reproducibility reports include

- ABMForge version or commit hash;
- Python version and operating system;
- installation method;
- exact commands run;
- scenario or experiment YAML snippet;
- `abmforge validate` output;
- relevant `manifest.json` fields;
- checksum mismatch messages when applicable;
- whether the archive was created before or after the current archive contract.
