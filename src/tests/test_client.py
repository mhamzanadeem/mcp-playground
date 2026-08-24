"""Integration tests for MCP discovery and invocation."""

from __future__ import annotations

import pytest

from mcp_client.client import MCPClient


@pytest.mark.asyncio
async def test_stdio_client_discovers_tool_and_calls_it() -> None:
    async with MCPClient() as client:
        tools = await client.list_tools()

        names = {
            tool.name
            for tool in tools
        }

        assert "get_current_weather" in names

        result = await client.call_tool(
            "get_current_weather",
            {
                "city": "Tokyo",
                "units": "metric",
            },
        )

        assert not result.is_error
        assert (
            result.structured_content["result"]["city"]
            == "Tokyo"
        )
        assert (
            result.structured_content["result"]["temperature"]
            == 27.0
        )


@pytest.mark.asyncio
async def test_resource_read() -> None:
    async with MCPClient() as client:
        greeting = await client.read_greeting("Ada")

        assert "Ada" in greeting
        assert "MCP resource" in greeting