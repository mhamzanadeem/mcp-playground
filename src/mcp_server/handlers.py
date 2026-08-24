"""MCP-facing handler helpers.

The official SDK owns JSON-RPC dispatch. This module keeps application-level
formatting/parsing separate from the server construction so it can be reused
by tests and clients.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import CallToolResult


def result_to_json(result: CallToolResult) -> str:
    """Render a typed MCP tool result for logs or agent input."""
    payload: dict[str, Any] = {
        "is_error": result.is_error,
        "content": [getattr(item, "text", repr(item)) for item in result.content],
    }
    structured = getattr(result, "structured_content", None)
    if structured:
        payload["structured_content"] = structured
    return json.dumps(payload, default=str, sort_keys=True)