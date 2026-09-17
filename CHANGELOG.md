# Changelog

All notable changes to Tokenomics will be documented here.

## Unreleased

### Added

- Provider-neutral, recommendation-only cost-aware planning with caller-supplied
  model profiles, capability/complexity checks, handoff-overhead accounting,
  optional minimum-savings alerts, and risk-based review gates.
- `tokenomics plan-savings` and the privacy-safe
  `tokenomics_plan_savings` MCP tool.

## 0.3.1 - 2026-09-16

### Changed

- Added an explicit production-hardening completion bar and release checklist.
- Added versioned SQLite migration handling with protection against opening a
  newer database in an older application release.
- Made knowledge-pack replacement atomic and retained the prior pack for local
  rollback.
- Restricted new local database and knowledge-pack files to the current user on
  POSIX systems.
- Added dashboard validation responses, CLI error handling, distribution-build
  verification, and CI formatting checks.

## 0.3.0

### Added

- Anthropic usage adapter and privacy-safe API capture
- Session usage aggregation and conservative rework detection
- Measured optimization outcomes and net-savings calculation
- Local read-only dashboard on loopback
- Versioned knowledge-pack loading and integrity-checked updates
- Privacy-safe community knowledge workflow
- MCP client configuration example
- Phase-by-phase engineering and security review record

### Security

- Provider capture never persists response content
- API capture is size-limited
- Knowledge updates require HTTPS, approved GitHub hosts, SHA-256 verification, schema validation, and size limits
- Dashboard launcher binds to `127.0.0.1`
- MCP exposes only bounded, privacy-safe domain data

## 0.2.0

### Added

- Persistent Token Loss Ledger
- Deterministic recommendations
- Optional local MCP server over stdio
- MCP tools for aggregate usage, findings, savings, and recommendations
- MCP resources for local summary and findings
- Unit tests for MCP exposure, privacy boundaries, ledger validation, and detector validation

### Changed

- Usage-event metadata is allowlisted to prevent accidental persistence of private content
- CLI analysis can record privacy-safe findings in the local Token Loss Ledger
- MCP result sizes are bounded to control model-context overhead

## 0.1.0

### Added

- Local usage event model and SQLite storage
- Provider-neutral token cost calculations
- Deterministic waste-pattern detection
- Initial recommendation engine
- Initial test suite and GitHub Actions CI
