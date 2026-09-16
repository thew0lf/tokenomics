# Production hardening baseline

This document defines the completion bar for hardening the current local-first
MVP. It does **not** add provider features, cloud services, automatic prompt
submission, or collection of private content.

## Scope

The release baseline is complete when each item below is implemented and
verified. A checked item is an implemented property, not an intention.

### Local data safety

- [x] The SQLite database and installed knowledge files are written privately
  for the current user on platforms that support POSIX permissions.
- [x] The application has an explicit, versioned schema migration mechanism.
- [x] Schema changes are forward-only, recorded locally, and fail clearly when
  a database is newer than the running application.
- [x] Knowledge-pack installation validates the candidate before replacing the
  active pack, writes atomically, and retains the prior pack for rollback.

### Reliability and operability

- [x] CLI input and user-facing errors are reported without Python tracebacks
  for expected invalid input and missing records.
- [x] The dashboard returns client errors for invalid request parameters rather
  than an internal-server error.
- [x] The documented Python support range is enforced in local verification.
- [x] The package can be built and installed from its distribution artifact.

### Supply-chain and release hygiene

- [x] Direct dependencies have bounded, compatible versions and the project
  documents how to reproduce the development environment.
- [x] CI verifies formatting/linting, tests, and package build on every
  supported Python version.
- [x] The repository includes a release checklist covering tests, compatibility,
  changelog, and security review.

## Explicit non-goals

- Capturing prompts, responses, code, paths, credentials, or other private
  content.
- A hosted telemetry, analytics, or knowledge-registry service.
- Transparent interception of AI-client traffic.
- New provider or Graphify integrations.

## Completion evidence

Before marking this work complete, run the documented verification commands on
Python 3.11, 3.12, and 3.13. The commands must pass from a clean environment,
and every checklist item above must have a corresponding automated test or a
documented manual release check.

## Completion record

Completed on 2026-09-16. Clean-environment verification passed on Python 3.11,
3.12, and 3.13: `ruff format --check .`, `ruff check .`, and `pytest -q`.
The distribution was built successfully, then its wheel was installed and its
CLI invoked from a fresh Python 3.13 environment.
