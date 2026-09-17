# Tokenomics MCP

Tokenomics exposes an optional local Model Context Protocol (MCP) server so an MCP-capable AI host can query Tokenomics without receiving private project data.

The implementation uses the current MCP Python SDK v2 line. The SDK's high-level server is `MCPServer`, with decorator-based tools and resources.

## Install

```bash
python -m pip install -e '.[mcp]'
```

The MCP dependency is optional. Core Tokenomics remains usable without it.

## Run

```bash
tokenomics-mcp
```

By default the server reads `.tokenomics/tokenomics.db`. Set `TOKENOMICS_DB` to use another local database:

```bash
TOKENOMICS_DB=/path/to/tokenomics.db tokenomics-mcp
```

The server uses stdio transport, keeping the first integration local to the machine.

## Exposed tools

| Tool | Purpose |
| --- | --- |
| `tokenomics_usage` | Aggregate token usage only |
| `tokenomics_findings` | Recent Token Loss Ledger observations |
| `tokenomics_savings` | Estimated versus measured savings |
| `tokenomics_recommendations` | Deterministic recommendations from local findings |
| `tokenomics_plan_savings` | Cost-aware executor and review-gate recommendation from caller-supplied profiles; supports a minimum-savings threshold |

## Exposed resources

- `tokenomics://summary`
- `tokenomics://findings`

## Privacy boundary

The MCP adapter deliberately does not expose:

- prompts or AI responses
- source code or file contents
- local filenames or paths
- environment variables or credentials
- personal messages or identifying information
- unrestricted SQL or filesystem access

MCP is an adapter over the Tokenomics domain layer. It does not become the domain layer and it does not grant the connected AI host arbitrary access to the local database.

The usage model is intentionally read-oriented. Recommendations are deterministic and derived from the local Token Loss Ledger rather than asking an external AI service to inspect private data.

`tokenomics_plan_savings` is also recommendation-only. It accepts a model-profile
JSON document containing prices and declared capabilities, plus aggregate token
estimates. It does not receive prompts, source code, or responses, and it does
not select or launch a model.

## Review requirements

Every MCP change should receive both review passes:

1. **Senior AI Engineer review**: tool boundaries, model-facing schemas, privacy, token economics, prompt/data-flow risks, and whether MCP itself creates unnecessary token overhead.
2. **Senior Software Engineer review**: API design, test coverage, error handling, dependency management, backwards compatibility, maintainability, and security.

Both reviews should be completed before an MCP change is merged.

## Validation

The test suite uses the MCP SDK's in-process `Client(MCPServer)` path to exercise tool discovery and tool calls without starting a subprocess or opening a network port. This keeps MCP integration tests local and deterministic.
