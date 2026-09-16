# Privacy Model

Privacy is an architectural constraint, not a promise added after implementation.

## Local by default

Raw AI conversations and private project data remain on the user's machine. The MVP should not require a cloud service, centralized database, or telemetry endpoint.

## Data that stays private

Tokenomics must treat the following as private by default:

- Prompt text
- AI response text
- Source code
- File contents
- Filenames and paths
- Environment variables
- API keys and credentials
- Personal messages
- Names, email addresses, and other identifying information
- Private conversation IDs

Usage events use a Tokenomics-generated random UUID4 as their local session identifier. Provider conversation IDs are not accepted as persisted session identifiers.

Usage metadata is allowlisted. Callers cannot add arbitrary metadata fields that could become a side channel for prompt, response, or project content.

## Public knowledge

Tokenomics can distribute generalized knowledge such as:

- Waste-pattern identifiers
- Detection thresholds
- Token ratios
- Timing characteristics
- Provider/model identifiers where appropriate
- Detection confidence
- Estimated savings formulas
- Recommendation outcomes in aggregate

These are knowledge artifacts, not copies of private conversations.

## MCP boundary

The optional MCP server is local and read-oriented. It exposes aggregate usage, privacy-safe findings, savings, and deterministic recommendations. It does not expose prompts, responses, source code, file contents, paths, credentials, arbitrary SQL, or unrestricted filesystem access.

## Future network features

If network functionality is introduced, it must be opt-in and schema-defined. The implementation should construct a new shareable record from approved fields rather than taking a private record and attempting to redact it.

The default should remain no telemetry.

## Team sharing

A future project mode may allow users to deliberately share distilled findings with a team. The sharing boundary should be explicit:

```text
Keep private -> local only
Share with team -> distilled project finding
Publish -> generalized knowledge candidate
```

A shared finding should never require sharing the transcript that produced it.
