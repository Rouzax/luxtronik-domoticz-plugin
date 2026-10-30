"""Health bar ranges drawn on Domoticz device cards. Pure: no Domoticz imports.

Domoticz 2026.4 draws coloured bands under a card's value from the device's Color field
(www/app/widgets/dzBar.js). Every edge here comes from the controller's own settings, the
WZSV manual, the Luxtronik manual or fault table, or Alpha Innotec guidance; a device with
no sourced edge gets no bar. Amber is used only where a source names a softer boundary.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional

from addresses import LuxtronikAddress

# Domoticz's own default bar colours (dzBar.js seedDefaults), so these bars look like ones a
# user drew by hand.
BAR_OK = "#66bb6a"
BAR_WARNING = "#ffa726"
BAR_CRITICAL = "#DF2D3A"

Band = Dict[str, Any]
DataStore = Dict[str, List[int]]


def supported(domoticz_version: str) -> bool:
    """Plugins can set bar ranges from Domoticz 2026.4. Before that the Color field accepted
    colour-switch state only and dropped anything else, so a written bar would never show."""
    match = re.match(r"(\d{4})\.(\d+)", domoticz_version or "")
    if not match:
        return False
    return (int(match.group(1)), int(match.group(2))) >= (2026, 4)


def _band(start: float, end: float, color: str) -> Band:
    return {"from": start, "to": end, "color": color}


def _param(data_store: DataStore, index: int) -> Optional[float]:
    """A controller setting in tenths. 0 means the parameter was not read, never a real limit."""
    try:
        raw = data_store["READ_PARAMS"][index]
    except (KeyError, IndexError):
        return None
    return raw / 10 if raw else None


def _hot_gas(data_store: DataStore) -> Optional[List[Band]]:
    # T-HG max: above it the controller stops the compressor (faults 704/714).
    limit = _param(data_store, LuxtronikAddress.HOT_GAS_MAX_SETTING)
    if limit is None:
        return None
    return [_band(0, limit, BAR_OK), _band(limit, limit + 10, BAR_CRITICAL)]


def _supply(data_store: DataStore) -> Optional[List[Band]]:
    # Vorlauf max: above it the compressor switches off. Below 16 °C heating water trips
    # fault 732 in cooling.
    limit = _param(data_store, LuxtronikAddress.FLOW_MAX_SETTING)
    if limit is None or limit <= 16:
        return None
    return [
        _band(10, 16, BAR_CRITICAL),
        _band(16, limit, BAR_OK),
        _band(limit, limit + 10, BAR_CRITICAL),
    ]


def _fixed(bands: List[Band]) -> Callable[[DataStore], List[Band]]:
    return lambda _data_store: bands


_COP = [_band(0, 1, BAR_CRITICAL), _band(1, 8, BAR_OK)]  # below 1: worse than direct electric

# unit -> (rule, drawn on a temperature card). Temperature cards read an object keyed by sensor,
# utility cards a bare array (dzBarService.loadForKey vs dzUtilityWidget.getBarRanges); the
# wrong shape draws nothing and logs nothing.
RULES: Dict[int, tuple] = {
    50: (_fixed(_COP), False),
    51: (_fixed(_COP), False),
    52: (_fixed(_COP), False),
    60: (_supply, True),
    # Hot water: below 50 °C is the legionella growth range (NL risk table); 65 °C is the
    # WZSV maximum with the electric heater.
    80: (
        _fixed([_band(30, 50, BAR_WARNING), _band(50, 65, BAR_OK), _band(65, 75, BAR_CRITICAL)]),
        True,
    ),
    160: (_hot_gas, True),
    # Superheat below 2 K for 5 minutes trips fault 765.
    165: (_fixed([_band(0, 2, BAR_CRITICAL), _band(2, 15, BAR_OK)]), False),
    # Alpha Innotec: runs under about 6 minutes cost efficiency, 30-60 minutes is uncritical.
    182: (
        _fixed([_band(0, 6, BAR_CRITICAL), _band(6, 30, BAR_WARNING), _band(30, 120, BAR_OK)]),
        False,
    ),
}


def payload(unit_id: int, data_store: DataStore) -> Optional[str]:
    """The Color value for a device's bar, or None when it has no sourced bar right now."""
    rule = RULES.get(unit_id)
    if rule is None:
        return None
    build, temperature = rule
    bands = build(data_store)
    if not bands:
        return None
    value: Any = {"temp": bands} if temperature else bands
    return json.dumps(value, separators=(",", ":"))
