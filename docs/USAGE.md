# Usage

Tokenomics is a local-first Python application. Core analysis does not call an AI service.

## Implemented CLI

```text
tokenomics init
tokenomics record
tokenomics capture
tokenomics analyze
tokenomics outcome
tokenomics report
tokenomics knowledge install
tokenomics-dashboard
tokenomics-mcp
```

### `tokenomics capture`

Captures a locally available Anthropic Messages API JSON response. Tokenomics extracts only usage counters and writes a privacy-safe event. Input is limited to 2 MiB and response content is never written to SQLite.

### `tokenomics analyze`

Runs deterministic detectors against supplied text and optional token measurements. Use `--record-losses` to persist findings in the Token Loss Ledger.

### `tokenomics outcome`

Records measured recommendation results:

```bash
tokenomics outcome LOSS_ID --actual-tokens-saved 720 --accepted
```

Use `--rejected` when the recommendation was not accepted. Actual savings must be non-negative.

### `tokenomics knowledge install`

Installs a public knowledge pack only after HTTPS host validation, SHA-256 verification, size checks, and JSON schema validation.

### `tokenomics-dashboard`

Runs the optional local dashboard on `127.0.0.1:8765`. It exposes aggregate usage, savings, and bounded findings.

### `tokenomics-mcp`

Runs the optional MCP server over local stdio. Use `examples/mcp-client.json` as a starting configuration for an MCP-capable local host.

## Findings

A finding should be understandable without reading a raw conversation. It should identify the pattern, evidence, estimated impact, confidence, and recommended action.

## Optimization workflow

1. Detect a likely waste pattern.
2. Explain the evidence.
3. Estimate potential savings.
4. Offer an optimization.
5. Let the user approve it.
6. Measure resulting usage.
7. Compare actual savings with the estimate.
8. Store the outcome locally.

## Privacy

Running Tokenomics should not require uploading conversations or project data. Usage records contain token counters and an allowlisted metadata set. See [PRIVACY.md](PRIVACY.md) and [KNOWLEDGE.md](KNOWLEDGE.md).
