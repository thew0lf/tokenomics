# Tokenomics Knowledge Registry

This directory contains versioned, privacy-safe knowledge used by Tokenomics to detect waste and recommend optimizations.

The registry must never contain raw user conversations or private project data.

## Structure

```text
knowledge/
├── pack.json      versioned index of every rule, with severity and category
├── patterns/      one file per rule: signals, problem, recommendation
├── rules/         detector trigger definitions
└── pricing.json
```

Every rule in `pack.json` has a matching `patterns/<id>.yml`, and the test suite
checks that. Categories follow the sections of the policy in
[docs/POLICY.md](../docs/POLICY.md): tiers, plan delegate review, briefs, context,
verification, shared resources and credentials.

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
