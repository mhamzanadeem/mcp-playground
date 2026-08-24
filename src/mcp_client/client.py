"""High-level stdio MCP client wrapper."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_server.handlers import result_to_json

logger = logging.getLogger(__name__)


class MCPClient:
    """Own an MCP server subprocess and expose convenient typed operations."""

    def __init__(self, server_path: Path | None = None) -> None:
        self.server_path = server_path or (
            Path(__file__).resolve().parents[1] / "mcp_server" / "server.py"
        )
        self._session: ClientSession | None = None
        self._stdio_context: Any = None
        self._stream_context: Any = None

    async def __aenter__(self) -> "MCPClient":
        # Explicitly pass the Python executable and project src path so the child
        # process imports the same source tree even when launched from elsewhere.
        env = {
            "PYTHONPATH": str(Path(__file__).resolve().parents[1])
        }

        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(self.server_path)],
            env=env,
            cwd=str(self.server_path.parents[1]),
        )

        self._stdio_context = stdio_client(parameters)
        read_stream, write_stream = await self._stdio_context.__aenter__()

        self._stream_context = ClientSession(read_stream, write_stream)
        self._session = await self._stream_context.__aenter__()

        logger.info("-> MCP initialize")
        initialize_result = await self._session.initialize()

        logger.info(
            "<- MCP initialize: server=%s protocol=%s",
            getattr(initialize_result.server_info, "name", "unknown"),
            initialize_result.protocol_version,
        )

        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._stream_context is not None:
            await self._stream_context.__aexit__(exc_type, exc, tb)

        if self._stdio_context is not None:
            await self._stdio_context.__aexit__(exc_type, exc, tb)

    def _require_session(self) -> ClientSession:
        if self._session is None:
            raise RuntimeError(
                "MCPClient must be used inside an async context manager"
            )

        return self._session

    async def list_tools(self) -> list[Any]:
        """Discover all tools exposed by the server."""
        session = self._require_session()

        logger.info("-> MCP tools/list")
        response = await session.list_tools()

        logger.info(
            "<- MCP tools/list: %s",
            [tool.name for tool in response.tools],
        )

        return list(response.tools)

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Call one MCP tool and return its typed result."""
        session = self._require_session()

        logger.info(
            "-> MCP tools/call name=%s arguments=%s",
            tool_name,
            json.dumps(arguments, sort_keys=True),
        )

        result = await session.call_tool(tool_name, arguments)

        logger.info(
            "<- MCP tools/call result=%s",
            result_to_json(result),
        )

        return result

    async def read_greeting(self, name: str) -> str:
        """Read the example resource to demonstrate resources/read."""
        session = self._require_session()

        logger.info(
            "-> MCP resources/read uri=greeting://%s",
            name,
        )

        result = await session.read_resource(f"greeting://{name}")

        text_parts = [
            getattr(item, "text", "")
            for item in result.contents
        ]

        text = "".join(text_parts)

        logger.info(
            "<- MCP resources/read result=%s",
            text,
        )

        return text