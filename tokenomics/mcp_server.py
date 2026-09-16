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
    from mcp.server.mcpserver import MCPServer
except ImportError as exc:  # pragma: no cover - exercised by optional dependency installs
    raise RuntimeError(
        "The MCP extra is required. Install Tokenomics with 'pip install -e .[mcp]'."
    ) from exc

from .recommendations import _ACTIONS
from .storage import EventStore


def build_server(db_path: str | Path = ".tokenomics/tokenomics.db") -> MCPServer:
    """Build a read-only MCP server backed by the local Tokenomics store."""
    store = EventStore(db_path)
    mcp = MCPServer("Tokenomics")

    @mcp.tool()
    def tokenomics_usage() -> dict[str, Any]:
        """Return aggregate local token usage. No conversation content is returned."""
        return {"events": store.count(), **store.totals()}

    @mcp.tool()
    def tokenomics_findings(limit: int = 50) -> list[dict[str, object]]:
        """Return recent local Token Loss Ledger observations."""
        return store.losses(limit)

    @mcp.tool()
    def tokenomics_savings() -> dict[str, int]:
        """Return estimated versus measured token savings from the local ledger."""
        return store.savings()

    @mcp.tool()
    def tokenomics_recommendations(limit: int = 50) -> list[dict[str, object]]:
        """Return deterministic recommendations for recent ledger findings."""
        findings = store.losses(limit)
        results: list[dict[str, object]] = []
        for finding in findings:
            action, rationale = _ACTIONS.get(
                finding["loss_type"],
                (
                    "Review the interaction for avoidable repeated work.",
                    "Potential token waste was detected.",
                ),
            )
            results.append(
                {
                    "finding_id": finding["id"],
                    "loss_type": finding["loss_type"],
                    "action": action,
                    "rationale": rationale,
                    "estimated_savings_tokens": finding["estimated_tokens"],
                }
            )
        return results

    @mcp.resource("tokenomics://summary")
    def summary() -> str:
        """Expose a compact local summary for an MCP host to load as context."""
        return json.dumps(
            {
                "usage": {"events": store.count(), **store.totals()},
                "savings": store.savings(),
                "finding_count": store.loss_count(),
                "privacy": "local-only; raw conversation and project content are not exposed",
            },
            sort_keys=True,
        )

    @mcp.resource("tokenomics://findings")
    def findings_resource() -> str:
        """Expose recent privacy-safe Token Loss Ledger observations."""
        return json.dumps(store.losses(), sort_keys=True)

    return mcp


def main() -> None:
    """Run the local MCP server over stdio."""
    db_path = os.environ.get("TOKENOMICS_DB", ".tokenomics/tokenomics.db")
    build_server(db_path).run(transport="stdio")


if __name__ == "__main__":  # pragma: no cover
    main()
