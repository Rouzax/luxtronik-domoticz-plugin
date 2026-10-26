"""Last fault, firmware and heat pump type devices, and the new-fault notification."""

import time

import domoticz_stub as stub
import pytest

import context
import plugin
from device_specs_table import build_device_specs
from translations import Language

FAULT_TIME = 1657883911  # 2022-07-15 11:18:31 UTC, 13:18 in Amsterdam


@pytest.fixture(autouse=True)
def _amsterdam(monkeypatch):
    # Fault times are UTC epochs shown in Domoticz's local time.
    monkeypatch.setenv("TZ", "Europe/Amsterdam")
    time.tzset()
    yield
    monkeypatch.delenv("TZ")
    time.tzset()


class _Translator(context._PassthroughTranslator):
    def __init__(self, language):
        self.language = language


def calc(**values):
    arr = [0] * 300
    for index, value in values.items():
        arr[int(index[1:])] = value
    return {"READ_CALCUL": arr}


def _spec(unit_id):
    return next(s for s in build_device_specs() if s.unit_id == unit_id)


def _read(unit_id, store, language=Language.ENGLISH, monkeypatch=None):
    context.translator = _Translator(language)
    try:
        spec = _spec(unit_id)
        return spec.read_converter.convert(store, spec.command, spec.address, *spec.read_args)
    finally:
        context.translator = context._PassthroughTranslator()


def test_last_fault_shows_code_message_and_local_time():
    result = _read(203, calc(c100=790, c95=FAULT_TIME))
    assert result == {"nValue": 0, "sValue": "790: Severe inverter fault (2022-07-15 13:18)"}


def test_last_fault_in_dutch_uses_the_manual_text():
    result = _read(203, calc(c100=790, c95=FAULT_TIME), Language.DUTCH)
    assert result["sValue"] == "790: Ernstige inverter fout (2022-07-15 13:18)"


def test_last_fault_in_french_falls_back_to_english():
    result = _read(203, calc(c100=701, c95=FAULT_TIME), Language.FRENCH)
    assert result["sValue"] == "701: Error low pressure (2022-07-15 13:18)"


def test_unknown_fault_code_still_shows_code_and_time():
    result = _read(203, calc(c100=799 + 100, c95=FAULT_TIME))
    assert result["sValue"] == "899: Unknown fault (2022-07-15 13:18)"


def test_no_fault_recorded():
    assert _read(203, calc(c100=0, c95=0))["sValue"] == "No faults"


def test_firmware_version_from_characters():
    chars = {f"c{81 + i}": ord(ch) for i, ch in enumerate("V3.92.3")}
    assert _read(204, calc(**chars)) == {"nValue": 0, "sValue": "V3.92.3"}


def test_heatpump_type_known_and_unknown_code():
    assert _read(205, calc(c78=80))["sValue"] == "MSW2-9S"
    assert _read(205, calc(c78=999))["sValue"] == "Code 999"


def test_new_devices_in_the_table():
    used = {s.unit_id: s.device_params.get("Used") for s in build_device_specs()}
    assert (used[203], used[204], used[205]) == (1, 0, 0)
    assert all(_spec(u).device_params["TypeName"] == "Text" for u in (203, 204, 205))


# --- new-fault notification -------------------------------------------------


@pytest.fixture
def lux():
    stub.reset()
    p = plugin.LuxtronikPlugin()
    p._load_state()
    return p


def test_fault_present_at_first_start_is_recorded_not_announced(lux):
    lux._check_new_fault(calc(c100=790, c95=FAULT_TIME))
    assert stub.calls["notification"] == []
    assert stub.Configuration()["fault_seen"] == f"790@{FAULT_TIME}"


def test_same_fault_is_not_announced_again(lux):
    lux._check_new_fault(calc(c100=790, c95=FAULT_TIME))
    lux._check_new_fault(calc(c100=790, c95=FAULT_TIME))
    assert stub.calls["notification"] == []


def test_new_fault_is_announced_once_and_survives_restart(lux):
    lux._check_new_fault(calc(c100=790, c95=FAULT_TIME))
    later = FAULT_TIME + 86400
    lux._check_new_fault(calc(c100=701, c95=later))
    assert len(stub.calls["notification"]) == 1
    subject, body = stub.calls["notification"][0][:2]
    assert "701" in subject and "701" in body
    assert any("701" in m for m in stub.calls["error"])

    restarted = plugin.LuxtronikPlugin()
    restarted._load_state()
    restarted._check_new_fault(calc(c100=701, c95=later))
    assert len(stub.calls["notification"]) == 1


def test_no_fault_sends_nothing(lux):
    lux._check_new_fault(calc(c100=0, c95=0))
    assert stub.calls["notification"] == []
