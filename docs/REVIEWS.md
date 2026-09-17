# Engineering and Security Reviews

Tokenomics uses two engineering review lenses and an explicit security check at every phase boundary.

## Review standard

### Senior AI Engineer
- Token economics and optimization validity
- Model-facing interfaces and context boundaries
- Measurement and evaluation integrity
- AI overhead versus expected savings
- Privacy implications of model/tool interactions

### Senior Software Engineer
- Architecture and API correctness
- Error handling and failure modes
- Test coverage and regression risk
- Dependency and supply-chain hygiene
- Security, maintainability, and backwards compatibility

### Security review

Each phase checks data exposure, secrets, filesystem/network access, input validation, resource limits, dependency/update behavior, and tool authorization boundaries.

## Phase 1: Local observability

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Review result: local-only event/ledger model and deterministic analysis are appropriately separated from model calls.
- Security result: raw conversation content is outside the persistence model and metadata is allowlisted.

## Phase 2: Provider integrations

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Review result: provider adapters extract usage rather than conversation content; session aggregation remains provider-neutral.
- Security result: API responses are not persisted wholesale; CLI capture has a 2 MiB input limit and only usage fields enter SQLite.

## Phase 3: Optimization measurement loop

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Review result: realized savings are distinct from estimates, rework detection is explicitly conservative, and Tokenomics overhead can be subtracted from savings.
- Security result: outcome writes accept only a known loss ID and non-negative measured savings.

## Phase 4: Local dashboard

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Review result: dashboard is read-only over the domain store and exposes aggregate usage, findings, and savings rather than raw content.
- Security result: the supplied launcher binds only to `127.0.0.1`; no dashboard endpoint performs arbitrary SQL or filesystem access.

## Phase 5: Community knowledge

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Review result: public knowledge is separated from private usage data and updates are independently versioned.
- Security result: updates require HTTPS from approved GitHub hosts, a SHA-256 digest, schema validation, and a 2 MiB size limit before installation.

## Phase 6: MCP

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Review result: MCP is a thin, read-oriented adapter with bounded results and deterministic recommendations; it does not require model calls.
- Security result: no raw prompts, responses, files, credentials, arbitrary SQL, or unrestricted filesystem access are exposed.

## Final phase-gate result

**All planned phases passed the two engineering review lenses and the explicit security check.**

Reviews are phase gates, not a substitute for automated tests or CI. Subsequent changes must repeat the appropriate review and security checks.

## Production hardening baseline: 2026-09-16

This review covers the hardening baseline documented in
`PRODUCTION_HARDENING.md`. It is a role-based engineering review performed
against the implementation and verification evidence; it is not an external
security certification or a guarantee that future integrations are secure.

### Senior AI Engineer review: **PASS**

- The changes do not add model calls, new provider capture, automatic prompt
  submission, or new data egress.
- Tokenomics still distinguishes measured savings from estimates, and its
  current overhead calculation remains explicitly token-based.
- The provider, dashboard, knowledge, and MCP boundaries continue to exclude
  raw prompts, responses, and project content.

### Senior Software Engineer review: **PASS**

- SQLite schema versioning is forward-only, recorded through `PRAGMA
  user_version`, and fails safely when an older program sees a newer database.
- Knowledge updates validate before activation, replace atomically, retain a
  previous pack for recovery, and are covered by tests.
- Expected CLI and dashboard validation failures return bounded user-facing
  errors; tests cover the new behavior.

### DevOps review: **PASS**

- CI runs formatting, linting, tests, and a distribution build on Python 3.11,
  3.12, and 3.13.
- The release checklist requires a clean wheel-install verification and a
  privacy/compatibility review.
- Clean-environment checks passed on all supported Python versions; the built
  wheel installed and its CLI started successfully.

### Security specialist review: **PASS**

- Newly created databases and knowledge packs are user-readable only on POSIX
  platforms; no broad existing directory permissions are changed.
- The migration path rejects incompatible newer databases rather than risking
  downgrade corruption.
- Knowledge updates remain HTTPS-host restricted, size limited, digest checked,
  schema validated, and now avoid partial active-file replacement.
- The dashboard remains loopback-bound and read-only; MCP remains bounded and
  exposes no arbitrary SQL, filesystem, raw-content, or credential access.

### Technical writer review: **PASS after corrections**

- Reviewed README, contribution/release instructions, security guidance, MVP,
  architecture, usage, updating, knowledge, MCP, privacy, and review records.
- Corrected architecture claims to match the actual SQLite model, detector set,
  recommendation behavior, and token-only overhead accounting.
- Added the knowledge rollback instructions and reconciled the README's future
  work wording with the completed hardening baseline.

### Release decision

**PASS.** The defined MVP production-hardening baseline and its required review
lenses are complete. Remaining work is feature expansion and any additional
production requirements a future deployment model introduces.

## Cost-aware planning recommendations: 2026-09-17

This feature is decision support for a host's planning step. It recommends a
declared-capable lower-cost executor only when the caller-supplied estimate
remains lower after handoff overhead; it never dispatches, switches, or stops
model work.

### Senior AI Engineer review: **PASS**

- Pricing, capabilities, complexity ceilings, and token estimates are explicit
  caller-supplied inputs rather than claims inferred from a model or provider.
- The policy counts handoff input overhead and supports a caller-selected
  minimum-savings threshold, preventing a misleading recommendation based on
  a tiny nominal saving.
- The output makes its recommendation-only status and required review lenses
  explicit. No prompt, response, source-code, or private-context input exists.

### Senior Software Engineer review: **PASS**

- The policy is provider-neutral and isolated from storage and dispatch code.
- Profile parsing validates required fields, finite non-negative prices,
  capability declarations, complexity, and token counts.
- The CLI and MCP adapters use the same domain function; unit coverage includes
  a cheaper capable candidate, an incapable candidate, review gates, invalid
  profiles, and CLI output.

### Security specialist review: **PASS**

- The MCP tool accepts only caller-supplied profile JSON and aggregate numeric
  estimates. It has no filesystem, database, provider, subprocess, or model
  dispatch capability.
- The output contains price estimates and review labels only. Existing MCP
  restrictions against raw content, arbitrary SQL, credentials, and paths are
  unchanged.

### Architecture and DevOps review: **NOT REQUIRED**

- This is an additive local policy module with no service topology, deployment,
  schema, dependency, CI, or release-process change. Those review lenses are
  required when a future host adapter performs dispatch or introduces a new
  deployment boundary.

### Technical writer review: **PASS**

- The README, CLI/MCP reference, profile example, and dedicated planning guide
  consistently describe the feature as recommendation-only and distinguish
  illustrative prices from approved production pricing.
