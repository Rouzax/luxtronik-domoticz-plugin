"""Run-time counters: controller totals as Domoticz counters with day/week/month history."""

import domoticz_stub as stub
import pytest

import domoticz_api
import plugin
from device_specs_table import build_device_specs

DEVICE_ID = "luxtronikex_hw18"
# unit -> (calc address, used by default, stores minutes)
COUNTERS = {
    186: (56, 1, True),  # compressor
    187: (57, 1, False),  # compressor starts
    188: (64, 1, True),  # heating
    189: (65, 1, True),  # hot water
    190: (60, 1, True),  # backup heater 1
    191: (66, 0, True),  # cooling
    192: (63, 0, True),  # heat pump
}


def _spec(unit_id):
    return next(s for s in build_device_specs() if s.unit_id == unit_id)


def _calc(**values):
    arr = [0] * 300
    for index, value in values.items():
        arr[int(index[1:])] = value
    return {"READ_CALCUL": arr}


def _read(unit_id, store):
    spec = _spec(unit_id)
    return spec.read_converter.convert(store, spec.command, spec.address, *spec.read_args)


@pytest.fixture
def lux(monkeypatch):
    stub.reset()
    monkeypatch.setattr(plugin, "Devices", stub.Devices, raising=False)
    monkeypatch.setattr(plugin, "Parameters", {"Name": "HP"}, raising=False)
    p = plugin.LuxtronikPlugin()
    p._device_id = DEVICE_ID
    return p


@pytest.fixture
def divider_core(monkeypatch):
    """A Domoticz whose plugin Unit can store a counter divider."""
    monkeypatch.setattr(stub.Unit, "Adjustment2", 0.0, raising=False)


def _unit(unit_id):
    return stub.Devices[DEVICE_ID].Units[unit_id]


@pytest.mark.parametrize("unit_id", sorted(COUNTERS))
def test_counters_are_plain_domoticz_counters(unit_id):
    spec = _spec(unit_id)
    address, used, _ = COUNTERS[unit_id]
    params = spec.device_params
    assert (params["Type"], params["Subtype"], params["Switchtype"]) == (113, 0, 3)
    assert spec.command == "READ_CALCUL" and spec.address == address
    assert params["Used"] == used


def test_seconds_are_stored_as_whole_minutes():
    assert _read(188, _calc(c64=7259)) == {"nValue": 0, "sValue": "120"}


def test_starts_are_stored_as_counted():
    assert _read(187, _calc(c57=1234)) == {"nValue": 0, "sValue": "1234"}


@pytest.mark.parametrize("store", [_calc(c64=0), {"READ_CALCUL": [1, 2, 3]}, {}])
def test_missing_or_zero_total_skips_the_update(store):
    # Sending 0 would look like a counter reset to Domoticz, and the next real total
    # would then count as usage for that day.
    assert _read(188, store) is None


def test_supports_counter_divider_follows_the_framework(monkeypatch):
    assert domoticz_api.supports_counter_divider() is False
    monkeypatch.setattr(stub.Unit, "Adjustment2", 0.0, raising=False)
    assert domoticz_api.supports_counter_divider() is True


def test_older_domoticz_shows_minutes(lux):
    lux.create_devices()
    unit = _unit(188)
    assert unit.params["Options"]["ValueUnits"] == "min"
    assert "Adjustment2" not in vars(unit)


def test_divider_capable_domoticz_shows_hours(lux, divider_core):
    lux.create_devices()
    unit = _unit(188)
    assert unit.params["Options"]["ValueUnits"] == "h"
    assert unit.Adjustment2 == 60


def test_starts_never_get_a_divider(lux, divider_core):
    lux.create_devices()
    assert "Adjustment2" not in vars(_unit(187))


def test_existing_counter_keeps_the_users_unit_and_divider(lux, divider_core):
    lux.create_devices()
    unit = _unit(188)
    unit.Options = {"ValueQuantity": "Time", "ValueUnits": "min"}
    unit.Adjustment2 = 1.0

    lux.create_devices()

    assert _unit(188) is unit
    assert unit.Options["ValueUnits"] == "min" and unit.Adjustment2 == 1.0
