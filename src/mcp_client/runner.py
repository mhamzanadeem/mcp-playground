"""Command-line entry point for the end-to-end MCP demo."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Make `python src/mcp_client/runner.py` work without installing the package.
SRC_DIR = Path(__file__).resolve().parents[1]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mcp_client.agent import run_agent  # noqa: E402
from mcp_client.client import MCPClient  # noqa: E402


def configure_logging() -> None:
    """Send demo logs to stderr so they are visible without affecting MCP stdio."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


async def main() -> None:
    """Run the full subprocess -> MCP -> agent -> tool -> answer flow."""
    load_dotenv()
    configure_logging()

    question = os.getenv(
        "DEMO_QUESTION",
        "What's the weather in London?",
    )

    async with MCPClient() as mcp_client:
        answer = await run_agent(
            question,
            mcp_client,
        )

        print(f"\nAssistant: {answer}")


if __name__ == "__main__":
    asyncio.run(main())