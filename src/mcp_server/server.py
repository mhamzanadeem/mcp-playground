"""Executable MCP server using the official Python SDK."""

from __future__ import annotations

from mcp.server import MCPServer

from mcp_server.tools import get_current_weather
from mcp_server.utils import configure_logging

configure_logging()

# MCPServer is the SDK's high-level server API. It handles JSON-RPC 2.0,
# initialization, capability negotiation, validation, and stdio framing.
mcp = MCPServer(
    "mcp-demo-server",
    instructions=(
        "A teaching MCP server. Use get_current_weather for deterministic "
        "weather sample data and the greeting resource for a static greeting."
    ),
)

# The decorator turns the Python signature and docstring into a machine-readable
# MCP tool definition returned by tools/list.
mcp.add_tool(get_current_weather)


@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Return a static greeting resource."""
    return f"Hello, {name}! This response came from an MCP resource."


if __name__ == "__main__":
    # stdio is the default transport. stdout belongs to MCP protocol traffic;
    # logs are configured to stderr so they cannot corrupt the JSON-RPC stream.
    mcp.run(transport="stdio")