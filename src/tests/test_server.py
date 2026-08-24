"""Tests for the MCP server tool behavior."""

from __future__ import annotations

import pytest

from mcp_server.tools import get_current_weather


def test_weather_metric() -> None:
    result = get_current_weather(
        "London",
        "metric",
    )

    assert result.city == "London"
    assert result.temperature == 18.0
    assert result.units == "metric"


def test_weather_imperial() -> None:
    result = get_current_weather(
        "London",
        "imperial",
    )

    assert result.temperature == 64.4
    assert result.units == "imperial"


def test_unknown_city_is_controlled_error() -> None:
    with pytest.raises(
        ValueError,
        match="Unknown city",
    ):
        get_current_weather("Atlantis")