# Knowledge Packs

Tokenomics knowledge is public, versioned, and separate from private usage data.

## What may be shared

- detector identifiers
- generalized optimization rules
- aggregate token counts or ratios when deliberately contributed
- confidence and validation observations
- provider/model identifiers when safe to publish

## What must not be shared

- prompts or responses
- source code or file contents
- filenames or local paths
- API keys, credentials, environment variables
- personal messages or identifying information
- conversation IDs or repository URLs

## Update flow

1. A knowledge pack is published as versioned JSON.
2. The client downloads only over HTTPS from an approved GitHub host.
3. The client enforces a 2 MiB size limit.
4. The client verifies the expected SHA-256 digest.
5. The JSON schema is validated before installation.
6. The new pack replaces the local copy atomically only after validation. The
   previous pack is retained beside it with a `.previous` suffix for local,
   manual rollback.

To roll back, replace the active pack with its adjacent `.previous` file using
the filesystem tools appropriate to the local operating system. Rollback is a
local file recovery operation; it does not contact a network service.

The application binary and knowledge packs are separate update channels. Knowledge can evolve without silently replacing executable code.

## Contribution flow

Contributors should submit generalized rules or aggregate observations through a pull request. Reviewers should reject raw transcripts and private project data. A contribution should explain the pattern, evidence, expected effect, and how it was validated.
