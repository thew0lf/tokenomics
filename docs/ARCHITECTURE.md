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

SQLite is the planned MVP persistence layer. It stores usage events, sessions, findings, recommendations, and outcomes on the user's machine.

### Analyzer

The analyzer should prefer deterministic checks. Examples include repeated context, token growth, high-frequency calls, polling patterns, retry loops, excessive output, and signs of hidden failures.

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

Recommendations should be generated from local findings and versioned knowledge rules. User approval should be required before an optimization changes or resubmits an AI request.

### Outcome measurement

Tokenomics must compare predicted savings with actual results. This allows the local system to learn which recommendations work in a particular workflow.

## Net-savings requirement

Tokenomics must account for its own cost. Analysis should be throttled or skipped when the expected value of the analysis is lower than its own resource cost.

```text
net_savings = tokens_avoided - tokenomics_overhead
```

This applies whether the overhead is model tokens, CPU time, storage, or other measurable resources.

## Knowledge registry

Public knowledge is versioned separately from the application. A knowledge pack can contain generalized patterns, triggers, confidence information, and recommendations without containing private conversations.

Application releases and knowledge updates should therefore be independently manageable.
