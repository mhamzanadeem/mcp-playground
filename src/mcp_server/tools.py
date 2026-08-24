"""Application tools exposed through MCP."""

from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

Units = Literal["metric", "imperial"]


class WeatherResult(BaseModel):
    """Structured result returned by the weather MCP tool."""

    city: str
    temperature: float
    units: Units
    condition: str
    humidity_percent: int = Field(ge=0, le=100)


# Deterministic sample data keeps the demo runnable without a weather API key.
_WEATHER: dict[str, tuple[float, str, int]] = {
    "london": (18.0, "partly cloudy", 72),
    "new york": (23.0, "sunny", 61),
    "tokyo": (27.0, "clear", 68),
    "sydney": (16.0, "light rain", 79),
    "rawalpindi": (31.0, "mostly sunny", 48),
}


def get_current_weather(city: str, units: Units = "metric") -> WeatherResult:
    """Return deterministic current-weather sample data for a city.

    In a production service this function could call a weather provider,
    database, or internal data service. The MCP-facing contract stays the same.
    """
    normalized = city.strip().lower()
    logger.info("weather lookup city=%s units=%s", city, units)

    if normalized not in _WEATHER:
        supported = ", ".join(sorted(name.title() for name in _WEATHER))
        raise ValueError(f"Unknown city {city!r}. Supported cities: {supported}")

    celsius, condition, humidity = _WEATHER[normalized]
    temperature = celsius if units == "metric" else (celsius * 9 / 5) + 32

    return WeatherResult(
        city=city.strip().title(),
        temperature=round(temperature, 1),
        units=units,
        condition=condition,
        humidity_percent=humidity,
    )