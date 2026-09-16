# Tokenomics Knowledge Registry

This directory contains versioned, privacy-safe knowledge used by Tokenomics to detect waste and recommend optimizations.

The registry must never contain raw user conversations or private project data.

## Structure

```text
knowledge/
├── patterns/
├── providers/
└── optimization-rules/
```

## Pattern example

```yaml
pattern: ai_polling
trigger:
  ai_calls_per_minute: ">10"
  repeated_context_ratio: ">0.50"
problem: AI is being invoked repeatedly while monitoring a process.
recommendation: Perform monitoring locally and invoke AI only when meaningful state changes.
```

Patterns should include evidence or rationale where possible and should distinguish measured observations from estimates.
