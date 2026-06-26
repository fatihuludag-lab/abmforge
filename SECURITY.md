# Security Policy

ABMForge is an alpha-stage research software project. Security reports are
handled conservatively and privately where appropriate.

## Supported Versions

ABMForge does not yet have a stable 1.0 release.

Security fixes are expected to target the current `main` branch and the latest
published alpha release, when a release exists.

| Version | Supported |
| --- | --- |
| latest alpha | Yes |
| older alpha releases | Best effort |
| pre-alpha snapshots | No |

## Reporting a Vulnerability

Please do not open a public GitHub issue for a suspected security vulnerability.

Preferred reporting path:

1. contact the maintainer privately through the repository owner profile; or
2. use GitHub private vulnerability reporting if it is enabled for the repository.

Include:

- affected version or commit;
- operating system and Python version;
- a minimal reproduction, when safe;
- expected impact;
- whether the issue is already public.

## Scope

Security reports may include:

- unsafe file handling;
- archive path traversal;
- unsafe template generation;
- unsafe deserialization;
- command execution issues;
- accidental disclosure of local environment or sensitive paths.

Scientific model correctness issues, reproducibility bugs, and documentation
problems should usually be reported through normal GitHub issues instead.

## Response Expectations

This is a small research project. Response time may vary.

The maintainer will try to:

- acknowledge the report;
- confirm whether the issue is in scope;
- prepare a fix or mitigation;
- document the fix in release notes when appropriate.

## Current Security Non-Goals

ABMForge currently does not claim:

- sandboxed execution of user models;
- safe execution of untrusted model code;
- secure processing of untrusted archives;
- protection against malicious Python packages or plugins.

Users should only run model code and archives from sources they trust.
