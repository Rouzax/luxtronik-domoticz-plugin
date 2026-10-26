"""create_devices against the DomoticzEx stub, including units Domoticz refuses to create."""

import domoticz_stub as stub
import pytest

import plugin

REFUSED = {171, 172}


@pytest.fixture
def lux(monkeypatch):
    stub.reset()
    monkeypatch.setattr(plugin, "Devices", stub.Devices, raising=False)
    monkeypatch.setattr(plugin, "Parameters", {"Name": "HP"}, raising=False)
    p = plugin.LuxtronikPlugin()
    p._device_id = "luxtronikex_hw18"
    return p


def _refuse(monkeypatch, units):
    """Make the stub behave like Domoticz with 'Accept new devices' off for these units."""
    original = stub.Unit.Create

    def create(self):
        if self.Unit not in units:
            original(self)

    monkeypatch.setattr(stub.Unit, "Create", create)


def test_all_units_created_when_accepted(lux):
    lux.create_devices()
    units = stub.Devices["luxtronikex_hw18"].Units
    assert len(units) == 68
    assert not any("could not create" in m.lower() for m in stub.calls["status"])


def test_refused_units_are_not_reported_as_created(lux, monkeypatch):
    _refuse(monkeypatch, REFUSED)

    lux.create_devices()

    units = stub.Devices["luxtronikex_hw18"].Units
    assert REFUSED.isdisjoint(units) and len(units) == 68 - len(REFUSED)
    # Names are only recorded for devices that exist.
    for unit_id in REFUSED:
        assert f"luxtronikex_hw18:{unit_id}" not in lux._auto_names
    # One warning that names the refused units and how to allow them.
    warnings = [m for m in stub.calls["status"] if m.startswith("Warning:")]
    assert len(warnings) == 1
    assert "171" in warnings[0] and "172" in warnings[0]
    assert "new devices" in warnings[0]
