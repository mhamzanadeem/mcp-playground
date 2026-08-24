"""Shared Pydantic models used by the demo."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Units = Literal["metric", "imperial"]


class ToolCall(BaseModel):
    """A normalized tool call selected by the agent."""

    name: str
    arguments: dict[str, object]