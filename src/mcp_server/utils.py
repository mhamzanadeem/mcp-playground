"""Shared server utilities."""

from __future__ import annotations

import logging
import sys


def configure_logging() -> None:
    """Configure stderr logging so stdout remains reserved for MCP protocol traffic."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )