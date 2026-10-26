"""Working mode must show Idle when the compressor itself uses no power, even with pump
power compensation adding the circulation pumps to the power reading."""

import domoticz_stub as stub
import pytest

import plugin
from addresses import LuxtronikAddress as A
from device_specs_table import build_device_specs


@pytest.fixture
def lux():
    stub.reset()
    p = plugin.LuxtronikPlugin()
    p._configure_pump_compensation(True, ("2", "60", "3", "140"))
    return p


def _store(compressor_w, hup_pct, mode=0):
    calc = [0] * 300
    calc[A.POWER_TOTAL] = compressor_w
    calc[A.HEATING_PUMP_SPEED] = hup_pct
    calc[A.WORKING_MODE] = mode
    return {"READ_CALCUL": calc}


def _working_mode(store):
    spec = next(s for s in build_device_specs() if s.unit_id == 1)
    return spec.read_converter.convert(store, spec.command, spec.address, *spec.read_args)


def test_idle_when_only_the_pumps_run(lux):
    store = _store(compressor_w=0, hup_pct=66)
    lux._apply_pump_compensation(store)
    assert store["READ_CALCUL"][A.POWER_TOTAL] > 20  # compensated power includes the pump
    assert _working_mode(store)["sValue"] == "Idle"


def test_mode_shown_when_the_compressor_runs(lux):
    store = _store(compressor_w=1800, hup_pct=66, mode=1)
    lux._apply_pump_compensation(store)
    assert _working_mode(store)["sValue"] == "DHW"


def test_idle_without_compensation_still_works():
    store = _store(compressor_w=0, hup_pct=66)
    assert _working_mode(store)["sValue"] == "Idle"
