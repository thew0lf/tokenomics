import asyncio

from mcp import Client

from tokenomics.ledger import LossEvent, LossType
from tokenomics.mcp_server import build_server
from tokenomics.storage import EventStore


def test_mcp_server_exposes_only_safe_domain_surface(tmp_path):
    async def exercise() -> None:
        server = build_server(tmp_path / "tokenomics.db")
        async with Client(server) as client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            assert {tool.name for tool in tools.tools} == {"tokenomics_usage", "tokenomics_findings", "tokenomics_savings", "tokenomics_recommendations"}
            assert {str(resource.uri) for resource in resources.resources} == {"tokenomics://summary", "tokenomics://findings"}
    asyncio.run(exercise())


def test_mcp_server_uses_local_store(tmp_path):
    async def exercise() -> None:
        server = build_server(tmp_path / "tokenomics.db")
        async with Client(server) as client:
            result = await client.call_tool("tokenomics_usage", {})
            assert not result.is_error
            assert result.structured_content == {"events": 0, "input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0}
    asyncio.run(exercise())


def test_mcp_server_rejects_unbounded_result_requests(tmp_path):
    async def exercise() -> None:
        server = build_server(tmp_path / "tokenomics.db")
        async with Client(server) as client:
            result = await client.call_tool("tokenomics_findings", {"limit": 21})
            assert result.is_error
    asyncio.run(exercise())


def test_mcp_recommendations_map_loss_type_to_rule(tmp_path):
    db = tmp_path / "tokenomics.db"
    EventStore(db).add_loss(LossEvent(loss_type=LossType.POLLING, estimated_tokens=500, description="polling", confidence=0.9))

    async def exercise() -> None:
        async with Client(build_server(db)) as client:
            result = await client.call_tool("tokenomics_recommendations", {})
            assert not result.is_error
            assert "Monitor state locally" in result.content[0].text
    asyncio.run(exercise())
