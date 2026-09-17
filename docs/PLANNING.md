# Cost-aware planning recommendations

Tokenomics can assess a plan before implementation and recommend the lowest-cost
model that is declared capable of completing the work. It is a recommendation
only: Tokenomics does not select, start, stop, or hand off work to an AI model.

## What the assessment considers

- Caller-supplied input/output token prices for each model.
- Caller-declared task capabilities and maximum complexity for each model.
- Estimated input/output tokens for the implementation.
- Handoff-context overhead.
- Risk-based review gates.

The policy deliberately does not inspect prompts, source code, responses, or
private project context. It does not infer that a model is capable; that
information must be supplied and maintained by the user or host integration.

## Run locally

Create a local profile file using
[`examples/model-profiles.json`](../examples/model-profiles.json) as a template.
The example contains illustrative values only; replace them with your own
approved pricing and capability assessments.

```bash
tokenomics plan-savings \
  --profiles .tokenomics/model-profiles.json \
  --planner planning-model \
  --task-class implementation \
  --complexity medium \
  --input 12000 \
  --output 2000 \
  --handoff-overhead 1000 \
  --minimum-net-savings 0.05
```

The result reports the estimated cost of continuing with the planning model, the
estimated cost of an eligible lower-cost executor including handoff overhead,
net estimated savings, and the required review lenses.

`--minimum-net-savings` suppresses immaterial alerts. Its currency unit must
match the one used for your profile rates. The feature stores neither the
handoff context nor the task content used to create that estimate.

## Review gates

Every recommendation includes QA. Higher-complexity work adds Senior Software
Engineer review and, for high complexity, Architecture review. Documentation,
deployment, and security task classes respectively add Technical Writer, DevOps,
and Security Specialist review.

These gates are decision support, not claims that a review has already occurred.

## Host integrations

The optional MCP server exposes `tokenomics_plan_savings`. Hosts can turn that
tool into their own planning UI—for example a Claude Code slash/MCP prompt, a
Codex project skill, or a terminal-agent command—without changing this policy.
The host should offer the feature as an explicit planning preference, such as
“planning savings on/off,” and keep automatic model switching disabled by
default.
