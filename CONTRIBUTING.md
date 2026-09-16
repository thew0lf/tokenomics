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

Use a supported Python version (3.11, 3.12, or 3.13) and an isolated virtual environment:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
ruff format --check .
ruff check .
pytest -q
python -m build
```

The project deliberately uses compatible dependency ranges rather than a
committed lockfile because it is a library/CLI. The CI matrix is the supported
compatibility contract; changes to direct dependency bounds require testing on
all three supported Python versions.

## Release checklist

- Update `CHANGELOG.md` and user-facing documentation.
- Run formatting, linting, tests, and a distribution build on Python 3.11, 3.12,
  and 3.13.
- Verify an install from the built wheel in a fresh environment.
- Review changes against `SECURITY.md`, including privacy-boundary and local
  data compatibility implications.
- Confirm schema migrations and knowledge-pack updates have a documented
  recovery path.

Keep new modules small, testable, and understandable. Prefer a clear
implementation over premature abstraction.
