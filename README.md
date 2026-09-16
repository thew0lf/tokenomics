# Tokenomics

### An AI Token Efficiency Project by GGCLTMGT

> **Spend fewer tokens reaching a correct, verified result.**

Tokenomics is an open-source, privacy-first project for understanding where AI tokens are being spent, identifying avoidable waste, and helping engineers and students get to correct results with less rework.

## Privacy first

Tokenomics is designed around a simple rule: **private conversations and private project data stay private.**

Tokenomics does not upload, share, or centralize:

- AI prompts or conversations
- AI responses
- Source code or file contents
- Filenames or local paths
- Environment variables or secrets
- API keys or credentials
- Personal messages or identifying information

Analysis is local-first. Shared community knowledge consists of generalized detection rules, optimization strategies, and privacy-safe measurements, not people's conversations.

## What Tokenomics looks for

Tokenomics focuses on token waste that can often be detected without sending content to another service:

- Repeated or unnecessarily large context
- Rework caused by ambiguity or unchecked results
- Excessive output and pasted logs
- Polling and monitoring loops that repeatedly invoke AI
- Retry loops and recursive AI calls
- Hidden errors such as `2>/dev/null`
- Commands that hide failures through pipelines
- Unverified empty or zero-result queries
- Confusion between written, merged, released, and running states

The goal is not simply to count tokens. The goal is to understand **why** tokens were spent and whether the work actually produced a verified result.

## The Tokenomics loop

```text
CAPTURE
   ↓
MEASURE
   ↓
UNDERSTAND
   ↓
DETECT TOKEN LOSS
   ↓
RECOMMEND
   ↓
EXECUTE
   ↓
MEASURE AGAIN
   ↓
DID WE ACTUALLY SAVE?
   ↓
UPDATE THE MODEL
```

Tokenomics should measure **net savings**, including its own analysis overhead. A tool that consumes more tokens than it saves has failed its purpose.

## Shared knowledge without shared conversations

Tokenomics separates private usage data from public knowledge.

```text
                 Public Tokenomics Knowledge
                           ↓
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
         Student A     Student B     Student C
         local data    local data    local data
```

A useful discovery can become a generalized rule such as:

```yaml
pattern: ai_polling
signal:
  ai_calls_per_minute: ">10"
  repeated_context_ratio: ">0.50"
recommendation: invoke AI only when meaningful state changes
```

The rule can help everyone without exposing the conversation that produced it.

## Project status

**Early development.** The repository is being built from the core ideas of Tokenomics: local token observability, waste detection, measurable optimization, privacy, and community knowledge.

The first implementation target is Claude/Anthropic usage, with the architecture intended to remain vendor-neutral.

## Planned capabilities

1. Capture AI usage locally
2. Store usage events in local SQLite
3. Build sessions and timelines
4. Detect token-loss patterns
5. Estimate avoidable token usage
6. Explain why waste was detected
7. Suggest lower-cost approaches
8. Measure actual results against predicted savings
9. Provide a local dashboard and CLI
10. Maintain versioned community knowledge packs

## Repository layout

```text
tokenomics/
├── tokenomics/          # application code
├── knowledge/           # public detection rules and knowledge
├── docs/                # documentation
├── tests/               # automated tests
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── LICENSE
```

## Getting started

The implementation is being developed incrementally. Installation and usage instructions will be added as the first runnable CLI and local dashboard are introduced.

See:

- [Architecture](docs/ARCHITECTURE.md)
- [Privacy](docs/PRIVACY.md)
- [Usage](docs/USAGE.md)
- [Updating](docs/UPDATING.md)
- [Contributing](CONTRIBUTING.md)

## License

Tokenomics is open-source software licensed under the Apache License 2.0.

Copyright © 2026 GGCLTMGT.

See [LICENSE](LICENSE) for the complete license text.
