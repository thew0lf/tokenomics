# Engineering and Security Reviews

Tokenomics uses two review lenses at every phase boundary.

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

Each phase receives an explicit security check covering:
- Data exposure and privacy boundaries
- Secrets and credential handling
- Local filesystem and network access
- Input validation and resource limits
- Dependency and update behavior
- MCP/tool authorization boundaries

## Phase 1: Local observability

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Scope: local event model, SQLite persistence, deterministic detectors, recommendations, ledger, and privacy-safe metadata.

## Phase 2: Real AI integrations

- Senior AI Engineer review: **PENDING**
- Senior Software Engineer review: **PENDING**
- Security check: **PENDING**

## Phase 3: Optimization loop

- Senior AI Engineer review: **PENDING**
- Senior Software Engineer review: **PENDING**
- Security check: **PENDING**

## Phase 4: Local dashboard

- Senior AI Engineer review: **PENDING**
- Senior Software Engineer review: **PENDING**
- Security check: **PENDING**

## Phase 5: Community knowledge

- Senior AI Engineer review: **PENDING**
- Senior Software Engineer review: **PENDING**
- Security check: **PENDING**

## Phase 6: MCP

- Senior AI Engineer review: **PASS**
- Senior Software Engineer review: **PASS**
- Security check: **PASS**
- Scope: local stdio MCP adapter, narrow tools/resources, privacy boundary, result limits, and reference-client integration.

Reviews are phase gates, not a substitute for automated tests or CI.