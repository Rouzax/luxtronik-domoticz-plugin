"""Pure parsing of the Domoticz plugin Parameters dict into a typed config.

No Domoticz import: this operates on a plain dict so it is trivially testable.

Settings live in named manifest fields. Installs from before the named fields still have their
values in Mode1..Mode6: Domoticz keeps those columns, gives every new named field its manifest
default, and blanks Mode1..Mode6 only when the hardware page is next saved (the page sends an
empty value for a field the manifest no longer has). So any non-empty Mode field means the
user has not saved since upgrading, and the whole config is read from the old fields, which
hold their real values, instead of the named ones, which hold defaults.

Address, Port and the legacy Mode3 keep the original bracket/int() reads (raise on
missing/invalid); onStart's outer try/except handles the abort.
"""

from dataclasses import dataclass
from typing import Optional

from addresses import ConfigLimits
from update_check import CHANNELS

_LEGACY_FIELDS = tuple(f"Mode{n}" for n in range(1, 7))

# Labels match the manifest options, for the carry-over notice.
LANGUAGES = {"en": "English", "pl": "Polski", "nl": "Nederlands", "de": "Deutsch", "fr": "Français"}
_LEGACY_LANGUAGES = {"0": "en", "1": "pl", "2": "nl", "3": "de", "4": "fr"}

# HUP min, HUP max, VBO min, VBO max in watts, from the "circulation pump power consumption"
# row of the WZSV technical data tables. The 122 and 162 share their pumps.
PUMP_PRESETS = {
    "wzsv62": ("2", "60", "5", "87"),
    "wzsv92": ("2", "60", "3", "140"),
    "wzsv122": ("2", "60", "3", "180"),
    "wzsv162": ("2", "60", "3", "180"),
}
_PUMP_LABELS = {
    "wzsv62": "WZSV 62",
    "wzsv92": "WZSV 92",
    "wzsv122": "WZSV 122",
    "wzsv162": "WZSV 162",
}
_PUMP_RANGE_FIELDS = ("HupMinW", "HupMaxW", "VboMinW", "VboMaxW")
_PUMP_RANGE_NAMES = ("HUP min", "HUP max", "VBO min", "VBO max")

UPDATE_INTERVALS = (10, 15, 20, 30)
_DEBUG_LABELS = {
    0: "None",
    1: "Basic",
    3: "Basic + Device",
    5: "Basic + Comms",
    7: "Basic + Device + Comms",
    -1: "All",
}


@dataclass(frozen=True)
class PluginConfig:
    debug_level: int
    # A code from LANGUAGES, or an unrecognised legacy value the translator reports.
    language: str
    address: str
    port: int
    heartbeat_raw: int
    max_cop_raw: str
    # "off", a PUMP_PRESETS key, or "custom".
    pump_compensation: str
    # HUP min, HUP max, VBO min, VBO max in watts, unparsed: the plugin validates them.
    pump_ranges_raw: tuple[str, ...]
    update_check: str
    plugin_version: str
    from_legacy_fields: bool

    @property
    def pump_comp_enabled(self) -> bool:
        return self.pump_compensation != "off"


def _int_or(params: dict, key: str, default: int) -> int:
    try:
        return int(params[key])
    except (ValueError, TypeError, KeyError):
        return default


def _update_channel(params: dict) -> str:
    channel = params.get("UpdateCheck") or "auto"
    return channel if channel in CHANNELS else "auto"


def _named_language(params: dict) -> str:
    choice = params.get("DeviceLanguage") or "auto"
    if choice != "auto":
        return choice
    # Domoticz passes its own interface language as a code such as "nl" or "zh_TW".
    domoticz = (params.get("Language") or "").split("_")[0].lower()
    return domoticz if domoticz in LANGUAGES else "en"


def _named_pump(params: dict) -> tuple[str, tuple[str, ...]]:
    choice = params.get("PumpCompensation") or "off"
    if choice in PUMP_PRESETS:
        return choice, PUMP_PRESETS[choice]
    if choice == "custom":
        return choice, tuple(params.get(field, "") for field in _PUMP_RANGE_FIELDS)
    return "off", PUMP_PRESETS["wzsv92"]


def _legacy_pump(params: dict) -> tuple[str, tuple[str, ...]]:
    ranges = tuple(part.strip() for part in params.get("Mode5", "2,60,3,140").split(","))
    if params.get("Mode4", "0") != "1":
        return "off", ranges
    preset = next((key for key, values in PUMP_PRESETS.items() if values == ranges), "custom")
    return preset, ranges


def read_plugin_config(params: dict) -> PluginConfig:
    common = {
        "address": params["Address"],
        "port": int(params["Port"]),
        # The legacy manifest had no update-check setting, so the named field always applies.
        "update_check": _update_channel(params),
        "plugin_version": params.get("Version", ""),
    }
    if any(params.get(field) for field in _LEGACY_FIELDS):
        pump, ranges = _legacy_pump(params)
        legacy_language: str = params["Mode3"]
        return PluginConfig(
            debug_level=_int_or(params, "Mode6", 0),
            language=_LEGACY_LANGUAGES.get(legacy_language, legacy_language),
            heartbeat_raw=_int_or(params, "Mode2", ConfigLimits.HEARTBEAT_DEFAULT),
            max_cop_raw=params.get("Mode1", "30"),
            pump_compensation=pump,
            pump_ranges_raw=ranges,
            from_legacy_fields=True,
            **common,
        )
    pump, ranges = _named_pump(params)
    return PluginConfig(
        # Dropdowns are stored empty until the hardware page is first saved after a field is
        # added, so an empty value falls back to the default like a missing one.
        debug_level=_int_or(params, "DebugLevel", 0),
        language=_named_language(params),
        heartbeat_raw=_int_or(params, "UpdateInterval", ConfigLimits.HEARTBEAT_DEFAULT),
        max_cop_raw=params.get("MaxCop", "30"),
        pump_compensation=pump,
        pump_ranges_raw=ranges,
        from_legacy_fields=False,
        **common,
    )


def _pump_label(cfg: PluginConfig) -> str:
    if not cfg.pump_comp_enabled:
        return "Off"
    if cfg.pump_compensation in PUMP_PRESETS:
        # Identical presets cannot be told apart from the old values alone.
        values = PUMP_PRESETS[cfg.pump_compensation]
        return " or ".join(_PUMP_LABELS[k] for k, v in PUMP_PRESETS.items() if v == values)
    ranges = ", ".join(
        f"{name} {value} W"
        for name, value in zip(_PUMP_RANGE_NAMES, cfg.pump_ranges_raw, strict=False)
    )
    return f"Custom: {ranges}"


def _interval_label(seconds: int) -> str:
    if seconds > ConfigLimits.HEARTBEAT_MAX:
        return f"{seconds} seconds (now limited to {ConfigLimits.HEARTBEAT_MAX})"
    if seconds not in UPDATE_INTERVALS:
        return f"{seconds} seconds (pick the nearest option)"
    return f"{seconds} seconds"


def carry_over_notice(cfg: PluginConfig) -> Optional[str]:
    """What the user must re-enter on the hardware page while the old fields are in use, or
    None once the named settings apply. Saving the page without re-entering these values
    replaces them with the defaults the page shows."""
    if not cfg.from_legacy_fields:
        return None
    values = [
        f"Max COP value = {cfg.max_cop_raw or '(empty)'}",
        f"Update interval = {_interval_label(cfg.heartbeat_raw)}",
        f"Language = {LANGUAGES.get(cfg.language, cfg.language)}",
        f"Pump power compensation = {_pump_label(cfg)}",
        f"Debug level = {_DEBUG_LABELS.get(cfg.debug_level, cfg.debug_level)}",
    ]
    return (
        "Settings moved to new fields in this version. Until you save the hardware page, the "
        "plugin keeps using your previous values. Open Setup > Hardware, select this plugin, "
        "choose them again and press Update; saving without doing so resets them to the "
        "defaults shown. Previous values: " + "; ".join(values)
    )
