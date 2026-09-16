"""Local MCP adapter for Tokenomics.

The MCP surface intentionally exposes aggregate usage, findings, savings, and
recommendations. It does not expose raw prompts, responses, source code, files,
paths, credentials, or arbitrary database access.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install Tokenomics with 'pip install -e .[mcp]'.") from exc

from .recommendations import recommendation_for_rule
from .storage import EventStore

_MAX_RESULTS = 20
_LOSS_TO_RULE = {
    "hidden_error": "hidden-errors",
    "verification": "pipeline-status",
    "polling": "ai-polling",
    "repeated_context": "repeated-context",
}


def _validate_limit(limit: int) -> int:
    if not 1 <= limit <= _MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {_MAX_RESULTS}")
    return limit


def build_server(db_path: str | Path = ".tokenomics/tokenomics.db") -> MCPServer:
    """Build a read-only MCP server backed by the local Tokenomics store."""
    store = EventStore(db_path)
    mcp = MCPServer("Tokenomics")

    @mcp.tool()
    def tokenomics_usage() -> dict[str, Any]:
        """Return aggregate local token usage. No conversation content is returned."""
        return {"events": store.count(), **store.totals()}

    @mcp.tool()
    def tokenomics_findings(limit: int = 20) -> list[dict[str, object]]:
        """Return recent local Token Loss Ledger observations."""
        return store.losses(_validate_limit(limit))

    @mcp.tool()
    def tokenomics_savings() -> dict[str, int]:
        """Return estimated versus measured token savings."""
        return store.savings()

    @mcp.tool()
    def tokenomics_recommendations(limit: int = 20) -> list[dict[str, object]]:
        """Return deterministic recommendations for recent findings."""
        findings = store.losses(_validate_limit(limit))
        results: list[dict[str, object]] = []
        for finding in findings:
            rule_id = _LOSS_TO_RULE.get(str(finding["loss_type"]), str(finding["loss_type"]))
            action, rationale = recommendation_for_rule(rule_id)
            results.append({
                "finding_id": finding["id"],
                "loss_type": finding["loss_type"],
                "action": action,
                "rationale": rationale,
                "estimated_savings_tokens": finding["estimated_tokens"],
            })
        return results

    @mcp.resource("tokenomics://summary")
    def summary() -> str:
        """Expose a compact local summary for an MCP host."""
        return json.dumps({
            "usage": {"events": store.count(), **store.totals()},
            "savings": store.savings(),
            "finding_count": store.loss_count(),
            "privacy": "local-only; raw conversation and project content are not exposed",
        }, sort_keys=True)

    @mcp.resource("tokenomics://findings")
    def findings_resource() -> str:
        """Expose recent privacy-safe Token Loss Ledger observations."""
        return json.dumps(store.losses(_MAX_RESULTS), sort_keys=True)

    return mcp


def main() -> None:
    db_path = os.environ.get("TOKENOMICS_DB", ".tokenomics/tokenomics.db")
    build_server(db_path).run(transport="stdio")


if __name__ == "__main__":
    main()
