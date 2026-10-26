"""Tests for the module-level ``onCommand`` write path in plugin.py.

DomoticzEx dispatches commands to the Unit, then Device, then the module-level
``onCommand`` function (see UpdateEventTarget in the Domoticz core). The plugin
relies on that final fallback, so these tests lock in its behavior:

    1. a valid selector command reaches the validated write path
    2. an out-of-range value is blocked before any write
    3. an unknown (DeviceID, Unit) is a safe no-op

All writes go through a mocked connection; no live Domoticz or heat pump is
required and no real WRITE_PARAMS is ever sent.
"""

from unittest.mock import MagicMock

import pytest

import plugin
from addresses import LuxtronikAddress, SocketCommand
from converters import AvailableWritesConverter, CommandToNumberConverter
from device_spec import DeviceSpec, Field

DEVICE_ID = "luxtronikex_hw18"
UNIT = 21


@pytest.fixture(autouse=True)
def _isolate_module_state():
    """Give every test a clean logger and module-level command state."""
    saved = (plugin._logger, dict(plugin._unit_specs), plugin._plugin_ref)
    plugin._logger = MagicMock()
    plugin._unit_specs = {}
    plugin._plugin_ref = None
    try:
        yield
    finally:
        plugin._logger, unit_specs, plugin._plugin_ref = saved
        plugin._unit_specs.clear()
        plugin._unit_specs.update(unit_specs)


def _make_plugin_ref(allowed_values):
    """Build a fake plugin instance exposing the surface onCommand touches."""
    ref = MagicMock()
    ref.available_writes = {LuxtronikAddress.COOLING_ENABLED: Field("Cooling", allowed_values)}
    return ref


def _register_spec(address=LuxtronikAddress.COOLING_ENABLED):
    """Register a writable selector spec for (DEVICE_ID, UNIT)."""
    spec = DeviceSpec(
        unit_id=UNIT,
        spec_id="cooling_enabled",
        command="READ_PARAMS",
        address=address,
        read_converter=MagicMock(),
        write_converter=CommandToNumberConverter(),
    )
    plugin._unit_specs[(DEVICE_ID, UNIT)] = spec
    return spec


def test_valid_command_writes_and_refreshes():
    plugin._plugin_ref = _make_plugin_ref(allowed_values=[0, 1])
    _register_spec()

    # 'On' -> CommandToNumberConverter -> value 1, which is allowed
    plugin.onCommand(DEVICE_ID, UNIT, "On", 0, "")

    plugin._plugin_ref.connection.execute_with_retry.assert_called_once_with(
        SocketCommand.WRITE_PARAMS, LuxtronikAddress.COOLING_ENABLED, 1
    )
    plugin._plugin_ref.update_all.assert_called_once()


def test_out_of_range_value_is_blocked():
    # Only 0 is permitted, so the converted value 1 must be rejected.
    plugin._plugin_ref = _make_plugin_ref(allowed_values=[0])
    _register_spec()

    plugin.onCommand(DEVICE_ID, UNIT, "On", 0, "")

    plugin._plugin_ref.connection.execute_with_retry.assert_not_called()
    plugin._plugin_ref.update_all.assert_not_called()
    plugin._logger.error.assert_called()


def test_address_not_in_available_writes_is_blocked():
    # Spec points at an address the pump did not advertise as writable.
    plugin._plugin_ref = _make_plugin_ref(allowed_values=[0, 1])
    _register_spec(address=LuxtronikAddress.HEATING_MODE)

    plugin.onCommand(DEVICE_ID, UNIT, "On", 0, "")

    plugin._plugin_ref.connection.execute_with_retry.assert_not_called()
    plugin._logger.error.assert_called()


def test_unknown_unit_is_noop():
    plugin._plugin_ref = _make_plugin_ref(allowed_values=[0, 1])
    # No spec registered for this unit.

    plugin.onCommand(DEVICE_ID, 999, "On", 0, "")

    plugin._plugin_ref.connection.execute_with_retry.assert_not_called()
    plugin._plugin_ref.update_all.assert_not_called()


SELECTOR_UNIT = 10


def _register_selector():
    """Register the Heating mode selector (levels 0..40 -> controller values 0..4)."""
    plugin._plugin_ref = MagicMock()
    plugin._plugin_ref.available_writes = {
        LuxtronikAddress.HEATING_MODE: Field("Heating mode", [0, 1, 2, 3, 4])
    }
    plugin._unit_specs[(DEVICE_ID, SELECTOR_UNIT)] = DeviceSpec(
        unit_id=SELECTOR_UNIT,
        spec_id="heating_mode",
        command="READ_PARAMS",
        address=LuxtronikAddress.HEATING_MODE,
        read_converter=MagicMock(),
        write_converter=AvailableWritesConverter(10, LuxtronikAddress.HEATING_MODE),
    )


def test_selector_level_writes_its_mode():
    _register_selector()

    plugin.onCommand(DEVICE_ID, SELECTOR_UNIT, "Set Level", 20, "")

    plugin._plugin_ref.connection.execute_with_retry.assert_called_once_with(
        SocketCommand.WRITE_PARAMS, LuxtronikAddress.HEATING_MODE, 2
    )


@pytest.mark.parametrize("level", [50, -10, 15, 5])
def test_selector_level_that_is_not_a_level_writes_nothing(level):
    # A level the selector does not have must never fall back to a valid mode:
    # that would silently switch the heat pump to Automatic or a neighbouring mode.
    _register_selector()

    plugin.onCommand(DEVICE_ID, SELECTOR_UNIT, "Set Level", level, "")

    plugin._plugin_ref.connection.execute_with_retry.assert_not_called()
    messages = " ".join(str(c.args[0]) for c in plugin._logger.error.call_args_list)
    assert "WRITE BLOCKED" in messages


@pytest.mark.parametrize("command, expected", [("On", 1), ("Off", 0)])
def test_cooling_on_and_off_write(command, expected):
    plugin._plugin_ref = _make_plugin_ref(allowed_values=[0, 1])
    _register_spec()

    plugin.onCommand(DEVICE_ID, UNIT, command, 0, "")

    plugin._plugin_ref.connection.execute_with_retry.assert_called_once_with(
        SocketCommand.WRITE_PARAMS, LuxtronikAddress.COOLING_ENABLED, expected
    )


@pytest.mark.parametrize("command", ["Set Level", "Stop", "on", ""])
def test_cooling_other_commands_write_nothing(command):
    # Any command other than exactly On/Off must not be read as Off: that would
    # switch cooling off on the heat pump because of a script error.
    plugin._plugin_ref = _make_plugin_ref(allowed_values=[0, 1])
    _register_spec()

    plugin.onCommand(DEVICE_ID, UNIT, command, 0, "")

    plugin._plugin_ref.connection.execute_with_retry.assert_not_called()
    messages = " ".join(str(c.args[0]) for c in plugin._logger.error.call_args_list)
    assert "WRITE BLOCKED" in messages
