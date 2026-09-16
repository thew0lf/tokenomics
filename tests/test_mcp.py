import asyncio

from tokenomics.mcp_server import build_server


def test_mcp_server_exposes_only_safe_domain_surface(tmp_path):
    server = build_server(tmp_path / "tokenomics.db")
    tools = asyncio.run(server.list_tools())
    resources = asyncio.run(server.list_resources())

    assert {tool.name for tool in tools} == {
        "tokenomics_usage",
        "tokenomics_findings",
        "tokenomics_savings",
        "tokenomics_recommendations",
    }
    assert {str(resource.uri) for resource in resources} == {
        "tokenomics://summary",
        "tokenomics://findings",
    }


def test_mcp_server_uses_local_store(tmp_path):
    server = build_server(tmp_path / "tokenomics.db")
    result = asyncio.run(server.call_tool("tokenomics_usage", {}))

    assert not result.is_error
    assert result.structured_content == {
        "events": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    }


def test_mcp_server_rejects_unbounded_result_requests(tmp_path):
    server = build_server(tmp_path / "tokenomics.db")
    result = asyncio.run(server.call_tool("tokenomics_findings", {"limit": 21}))

    assert result.is_error
    assert "limit must be between 1 and 20" in result.content[0].text
