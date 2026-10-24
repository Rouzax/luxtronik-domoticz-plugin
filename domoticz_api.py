# pyright: reportMissingImports=false
"""The single seam between the plugin and the Domoticz framework.

This is the only module that imports DomoticzEx. Everything the plugin needs from
the framework (logging, debug/heartbeat setup, device unit create/lookup) goes
through these functions. The framework-injected `devices` mapping is passed in by
the caller, because Domoticz injects Parameters/Devices/Settings into the plugin
entry module's namespace, not into this module.
"""

from typing import Any, Optional

import DomoticzEx as Domoticz


def log_status(message: str) -> None:
    Domoticz.Status(message)


def log_debug(message: str) -> None:
    Domoticz.Debug(message)


def log_error(message: str) -> None:
    Domoticz.Error(message)


def send_notification(subject: str, body: str) -> None:
    """Send through every notification system Domoticz has (an empty subsystem). Best effort:
    the caller has logged the event already, so a missing or failing notifier is ignored."""
    send = getattr(Domoticz, "SendNotification", None)
    if send is None:
        return
    try:
        # Positional: the keyword names differ between Domoticz versions.
        send(subject, body, 0, "", "", "")
    except Exception as e:
        Domoticz.Debug(f"SendNotification failed ({type(e).__name__})")


def set_debugging(mask: int) -> None:
    Domoticz.Debugging(mask)


def set_heartbeat(seconds: int) -> None:
    Domoticz.Heartbeat(seconds)


def unit_exists(devices, device_id: str, unit_id: int) -> bool:
    return device_id in devices and unit_id in devices[device_id].Units


def create_unit(device_id: str, unit_id: int, name: str, params: dict) -> Any:
    unit = Domoticz.Unit(Name=name, DeviceID=device_id, Unit=unit_id, **params)
    unit.Create()
    return unit


def get_unit(devices, device_id: str, unit_id: int) -> Any:
    return devices[device_id].Units[unit_id]


def load_state() -> Optional[dict]:
    """Return the persisted plugin state blob, or None if never saved / unreadable."""
    try:
        cfg = Domoticz.Configuration()
    except Exception:
        return None
    return cfg or None


def save_state(state: dict) -> None:
    """Persist the plugin state blob via Domoticz.Configuration()."""
    Domoticz.Configuration(state)
