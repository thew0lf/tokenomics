# Changelog

All notable changes to Tokenomics will be documented here.

## Unreleased

### Added

- Local usage event model and SQLite storage
- Provider-neutral token cost calculations
- Deterministic waste-pattern detection
- Persistent Token Loss Ledger
- Deterministic recommendation engine
- Optional local MCP server over stdio
- MCP tools for aggregate usage, findings, savings, and recommendations
- MCP resources for local summary and findings
- Unit tests for MCP exposure, privacy boundaries, ledger validation, and detector validation

### Changed

- Usage-event metadata is now allowlisted to prevent accidental persistence of private content
- CLI analysis can record privacy-safe findings in the local Token Loss Ledger
- MCP result sizes are bounded to control model-context overhead
- README roadmap and MVP documentation now track the completed foundation and remaining MCP work

### Planned

- Claude/Anthropic usage capture
- Provider adapter interface
- Session reconstruction
- Real cache/token metadata ingestion
- Versioned cost profiles and pricing data
- Recommendation approval and actual-vs-estimated savings tracking
- Rework detection across sessions
- Tokenomics self-overhead accounting
- Local dashboard
- Versioned Tokenomics Knowledge Registry
- MCP client configuration examples and reference-client integration tests
