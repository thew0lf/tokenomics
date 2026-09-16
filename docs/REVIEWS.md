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

## Phase 2: Real AI integrations

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Review result: provider adapters extract usage rather than conversation content; session aggregation remains provider-neutral.
- Security result: API responses are not persisted wholesale; CLI capture has a 2 MiB input limit and only usage fields enter SQLite.

## Phase 3: Optimization loop

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