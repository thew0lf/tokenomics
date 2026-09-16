# Contributing to Tokenomics

Thanks for helping build Tokenomics.

## Core principles

1. **Privacy first.** Never add private conversations, source code, secrets, credentials, or personal data to the project.
2. **Measure before optimizing.** A recommendation should be tied to an observable waste pattern.
3. **Verify outcomes.** Estimated savings are not the same as measured savings.
4. **Keep the scope focused.** Tokenomics should reduce avoidable AI token usage without creating more overhead than it saves.
5. **Prefer deterministic local analysis.** Do not invoke an AI model when a reliable local check can answer the question.

## Knowledge contributions

Community knowledge should describe generalized patterns and rules, not conversation transcripts.

Good contribution:

```yaml
pattern: repeated-context
trigger:
  repeated_context_ratio: ">0.50"
recommendation: keep stable context local and send only changed information
```

Do not submit:

- Prompt or response transcripts
- Source code copied from a private project
- File contents or local paths
- API keys, tokens, credentials, or environment variables
- Personal or identifying information

## Pull requests

Please explain:

- What problem is being addressed
- How the behavior was measured or detected
- What changed
- How the change was tested
- Whether documentation was updated
- Whether the change affects privacy or token overhead

For optimization work, include before/after measurements when practical.

## Development

The project is in early development. Keep new modules small, testable, and understandable. Prefer a clear implementation over premature abstraction.
