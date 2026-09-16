# Usage

Tokenomics is currently in early development. This document describes the intended MVP interface and behavior.

## Planned CLI

```text
tokenomics init
tokenomics claude
tokenomics analyze
tokenomics report
tokenomics dashboard
```

### `tokenomics init`

Creates the local Tokenomics configuration and SQLite data store.

### `tokenomics claude`

Starts the Claude/Anthropic usage capture workflow for the local environment.

### `tokenomics analyze`

Runs local analysis against captured events and records detected waste patterns.

### `tokenomics report`

Produces a summary of token usage, detected waste, estimated savings, actual savings, and Tokenomics overhead.

### `tokenomics dashboard`

Starts the planned local dashboard, intended to be accessible only from the local machine by default.

## Findings

A finding should be understandable without reading a raw conversation. It should identify the pattern, evidence, estimated impact, confidence, and recommended action.

## Optimization workflow

Tokenomics should not silently rewrite or resubmit a user's request. The intended workflow is:

1. Detect a likely waste pattern.
2. Explain the evidence.
3. Estimate the potential savings.
4. Offer an optimization.
5. Let the user approve it.
6. Measure the resulting usage.
7. Compare actual savings with the estimate.
8. Store the outcome locally.

## Privacy

Running Tokenomics should not require uploading conversations or project data. See [PRIVACY.md](PRIVACY.md).
