"""Health bar ranges on device cards: the bands, and when the plugin may write them."""

import json
from typing import Any

import domoticz_stub as stub
import pytest

import bar_ranges
import plugin
from bar_ranges import BAR_CRITICAL, BAR_OK, BAR_WARNING

DEVICE_ID = "luxtronikex_hw18"


def _store(calc=None, params=None):
    c = [0] * 300
    p = [0] * 1200
    for i, v in (calc or {}).items():
        c[i] = v
    for i, v in (params or {}).items():
        p[i] = v
    return {"READ_CALCUL": c, "READ_PARAMS": p}


# The user's controller: T-HG max 115, Vorlauf max 64.
LIVE = _store(params={94: 1150, 149: 640})


def _bands(unit_id, store=LIVE) -> Any:
    payload = bar_ranges.payload(unit_id, store)
    return None if payload is None else json.loads(payload)


def _edges(bands):
    return [(b["from"], b["to"], b["color"]) for b in bands]


@pytest.mark.parametrize(
    "version, supported",
    [
        ("2026.4 (build 18490)", True),
        ("2026.4", True),
        ("2027.1", True),
        ("2026.3", False),
        ("2026.1 (build 17000)", False),
        ("", False),
    ],
)
def test_bars_need_domoticz_2026_4(version, supported):
    assert bar_ranges.supported(version) is supported


def test_hot_gas_turns_red_at_the_controllers_own_limit():
    assert _edges(_bands(160)["temp"]) == [(0, 115.0, BAR_OK), (115.0, 125.0, BAR_CRITICAL)]


def test_supply_is_red_below_16_and_at_vorlauf_max():
    assert _edges(_bands(60)["temp"]) == [
        (10, 16, BAR_CRITICAL),
        (16, 64.0, BAR_OK),
        (64.0, 74.0, BAR_CRITICAL),
    ]


def test_fixed_bands_from_the_manuals():
    assert _edges(_bands(80)["temp"]) == [
        (30, 50, BAR_WARNING),
        (50, 65, BAR_OK),
        (65, 75, BAR_CRITICAL),
    ]
    assert _edges(_bands(165)) == [(0, 2, BAR_CRITICAL), (2, 15, BAR_OK)]
    assert _edges(_bands(182)) == [(0, 6, BAR_CRITICAL), (6, 30, BAR_WARNING), (30, 120, BAR_OK)]


@pytest.mark.parametrize("unit_id", [50, 51, 52])
def test_cop_is_red_below_one(unit_id):
    assert _edges(_bands(unit_id)) == [(0, 1, BAR_CRITICAL), (1, 8, BAR_OK)]


def test_limits_missing_from_the_controller_give_no_bar():
    calc_only = {"READ_CALCUL": [0] * 300}
    for unit_id in (160, 60):
        assert bar_ranges.payload(unit_id, calc_only) is None
    # A zero limit is an unread parameter, not a real 0 °C cut-off.
    assert bar_ranges.payload(160, _store(params={94: 0})) is None


@pytest.mark.parametrize("unit_id", [61, 100, 101, 106, 140])
def test_devices_without_a_sourced_bar_get_none(unit_id):
    # Return, brine and source flow were dropped after the live test: return is far above the
    # heating limit during every hot water run, an axis crossing zero is drawn from its centre,
    # and the flow sensor reads below the manual minimum in normal operation.
    assert bar_ranges.payload(unit_id, LIVE) is None


# --- Writing the bars ---------------------------------------------------------------------


@pytest.fixture
def lux(monkeypatch):
    stub.reset()
    monkeypatch.setattr(plugin, "Devices", stub.Devices, raising=False)
    monkeypatch.setattr(plugin, "Parameters", {"Name": "HP"}, raising=False)
    p = plugin.LuxtronikPlugin()
    p._device_id = DEVICE_ID
    p.create_devices()
    p._bars_supported = True  # as on Domoticz 2026.4
    return p


def _unit(unit_id):
    return stub.Devices[DEVICE_ID].Units[unit_id]


def test_bars_are_written_once_with_update_properties(lux):
    lux._sync_bar_ranges(LIVE)

    unit = _unit(160)
    assert json.loads(unit.Color)["temp"][-1]["from"] == 115.0
    assert unit.update_calls[-1] == {"Log": False, "UpdateProperties": True}

    calls = len(unit.update_calls)
    lux._sync_bar_ranges(LIVE)
    assert len(unit.update_calls) == calls


def test_a_changed_controller_limit_rewrites_the_plugins_own_bar(lux):
    lux._sync_bar_ranges(LIVE)
    raised = _store(params={94: 1200, 149: 640})

    lux._sync_bar_ranges(raised)

    assert json.loads(_unit(160).Color)["temp"][-1]["from"] == 120.0


def test_bars_the_user_drew_are_left_alone(lux):
    own = '{"temp":[{"from":0,"to":100,"color":"#123456"}]}'
    _unit(160).Color = own

    lux._sync_bar_ranges(LIVE)

    assert _unit(160).Color == own
    assert not _unit(160).update_calls


def test_bars_the_user_changed_after_the_plugin_are_left_alone(lux):
    lux._sync_bar_ranges(LIVE)
    _unit(160).Color = ""  # the user removed the bar in the edit dialog
    calls = len(_unit(160).update_calls)
    raised = _store(params={94: 1200, 149: 640})

    lux._sync_bar_ranges(raised)

    assert _unit(160).Color == ""
    assert len(_unit(160).update_calls) == calls


def test_older_domoticz_gets_no_bars(lux):
    lux._bars_supported = False

    lux._sync_bar_ranges(LIVE)

    assert _unit(160).Color == ""
    assert "color" not in lux._auto_names.get(f"{DEVICE_ID}:160", {})
