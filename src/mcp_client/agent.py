"""OpenAI agent loop backed by dynamically discovered MCP tools."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from mcp_client.client import MCPClient

logger = logging.getLogger(__name__)


def _as_openai_tool(tool: Any) -> dict[str, Any]:
    """Translate an MCP tool definition into an OpenAI function tool."""
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": tool.input_schema,
        "strict": False,
    }


def _extract_tool_calls(response: Any) -> list[Any]:
    """Return function-call output items from a Responses API result."""
    return [
        item
        for item in response.output
        if getattr(item, "type", None) == "function_call"
    ]


def _output_text(response: Any) -> str:
    """Read the convenience text output from a Responses API result."""
    return getattr(response, "output_text", "") or ""


async def run_agent(
    question: str,
    mcp_client: MCPClient,
) -> str:
    """Let the model choose among the server's discovered MCP tools."""
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError(
            "Set OPENAI_API_KEY in .env before running the AI demo."
        )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-4.1-mini",
    )

    client = OpenAI(api_key=api_key)

    # Important: the agent does not hard-code the weather tool.
    # It discovers whatever MCP server exposes through tools/list.
    mcp_tools = await mcp_client.list_tools()

    openai_tools = [
        _as_openai_tool(tool)
        for tool in mcp_tools
    ]

    logger.info("User: %s", question)

    response = client.responses.create(
        model=model,
        input=question,
        instructions=(
            "You are an agent demonstrating MCP. Use an available MCP "
            "function when it is appropriate. Do not invent tool results."
        ),
        tools=openai_tools,
    )

    # The Responses API can return one or more function calls. Each call is
    # routed back through MCP rather than calling the Python function directly.
    tool_outputs: list[dict[str, str]] = []

    for call in _extract_tool_calls(response):
        logger.info(
            "OpenAI requested tool: %s %s",
            call.name,
            call.arguments,
        )

        arguments = json.loads(call.arguments)

        mcp_result = await mcp_client.call_tool(
            call.name,
            arguments,
        )

        if mcp_result.is_error:
            output = json.dumps(
                {
                    "error": True,
                    "details": getattr(
                        mcp_result,
                        "content",
                        [],
                    ),
                },
                default=str,
            )
        else:
            structured = getattr(
                mcp_result,
                "structured_content",
                None,
            )

            if structured:
                output = json.dumps(
                    structured,
                    default=str,
                )
            else:
                output = json.dumps(
                    {
                        "content": [
                            getattr(item, "text", repr(item))
                            for item in mcp_result.content
                        ]
                    },
                    default=str,
                )

        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": output,
            }
        )

    if tool_outputs:
        follow_up = client.responses.create(
            model=model,
            input=tool_outputs,
            previous_response_id=response.id,
            tools=openai_tools,
        )

        answer = _output_text(follow_up)
    else:
        answer = _output_text(response)

    logger.info("Final: %s", answer)

    return answer