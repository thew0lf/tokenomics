# Architecture

Tokenomics is intended to be local-first and vendor-neutral, with Claude/Anthropic as the first implementation target.

## High-level flow

```text
AI Provider / Local Tool
          |
          v
       Capture
          |
          v
   Local Event Store
       (SQLite)
          |
          v
 Session + Timeline
          |
          v
 Local Analyzer
   |       |       |
   v       v       v
Rework   Context   Loops
   |       |       |
   +-------+-------+
           |
           v
    Token Loss Ledger
           |
           v
    Recommendation
           |
           v
       User Review
           |
           v
       Execution
           |
           v
     Outcome Measure
           |
           v
      Local Learning
```

## Components

### Capture

Captures usage metadata locally. The initial provider integration is Claude/Anthropic. The provider boundary should make it possible to add other AI systems later.

### Local event store

SQLite is the local MVP persistence layer. It stores privacy-safe usage events
and Token Loss Ledger observations on the user's machine. A loss observation can
record the user's decision and a measured outcome; recommendations are derived
locally rather than persisted as a separate record type.

### Analyzer

The analyzer prefers deterministic checks. The current implementation detects
repeated context from supplied token measurements, polling/repeated-execution
constructs, hidden errors, and pipeline-status hazards. Additional patterns are
future work rather than current detections.

### Token Loss Ledger

Each finding should explain:

- What happened
- Why it is considered waste
- Tokens affected
- Estimated avoidable tokens
- Confidence
- Recommended action
- Result after the action

### Recommendation engine

Recommendations are generated locally from findings and versioned knowledge
rules. Tokenomics does not change or resubmit an AI request; the user decides
whether to apply a recommendation outside the tool.

### Outcome measurement

Tokenomics must compare predicted savings with actual results. This allows the local system to learn which recommendations work in a particular workflow.

## Net-savings requirement

Tokenomics must account for its own cost. Analysis should be throttled or skipped when the expected value of the analysis is lower than its own resource cost.

```text
net_savings = tokens_avoided - tokenomics_overhead
```

The current implementation accounts for Tokenomics overhead expressed in tokens.
CPU time, storage, and other resource-cost accounting are future extensions.

## Knowledge registry

Public knowledge is versioned separately from the application. A knowledge pack can contain generalized patterns, triggers, confidence information, and recommendations without containing private conversations.

Application releases and knowledge updates should therefore be independently manageable.
