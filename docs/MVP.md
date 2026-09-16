# Tokenomics MVP

## Goal

The MVP proves the Tokenomics loop locally, without transmitting private conversations or project data.

```text
capture → measure → detect → recommend → record outcome → measure again
```

## Included

- Local SQLite usage events
- Input/output/cache token accounting
- Provider-neutral cost calculation from caller-supplied pricing
- Deterministic detection of hidden errors
- Detection of pipeline status hazards
- Detection of AI polling/repeated execution
- Detection of repeated context when token counts are available
- Privacy-safe findings and recommendations
- Privacy-safe metadata enforcement at the usage-event boundary
- Local Token Loss Ledger persistence
- Optional local MCP server exposing aggregate usage, findings, savings, and recommendations
- Automated unit tests
- GitHub Actions CI across supported Python versions

## Deliberately not included yet

- Automatic transmission of prompts or responses
- Automatic submission of optimized prompts
- Cloud database or centralized telemetry
- Provider credentials stored by Tokenomics
- Claims that an estimated saving is an actual saving
- Arbitrary filesystem, SQL, or conversation access through MCP

## Definition of done for the first usable release

A local user should be able to install Tokenomics, initialize a local store, record usage, analyze a workload for waste, see a recommendation, record the observation, and report measured usage without Tokenomics needing access to a cloud Tokenomics service.

The optional MCP integration must remain a thin, privacy-safe adapter over the same local domain layer. It must not expand access to private project data.

Actual savings must be measured from subsequent usage. Estimates are hypotheses, not results.
