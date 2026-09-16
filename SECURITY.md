# Security and Privacy

## Reporting a security issue

Please do not disclose security vulnerabilities in a public issue if the report contains sensitive information.

Use the repository's GitHub security reporting features when available. If private reporting is not available, avoid including secrets, credentials, private source code, or other sensitive material in the issue.

## Privacy boundary

Tokenomics is designed to keep private AI usage and project data local.

The project must not transmit raw:

- Prompts or AI responses
- Source code or file contents
- Local filenames or paths
- Environment variables
- API keys or credentials
- Personal messages or identifying information
- Private conversation identifiers

Future network features must use an explicit, documented allowlist of data that can leave the machine. Redaction alone is not considered a sufficient privacy boundary for raw conversation data.

## Knowledge registry

Public knowledge should contain generalized patterns, rules, measurements, and strategies. It must not require uploading the private interaction that produced a finding.
