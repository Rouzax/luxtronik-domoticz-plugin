from device_spec import DeviceSpec
from device_specs_table import build_device_specs


def test_returns_nonempty_list_of_devicespec():
    specs = build_device_specs()
    assert isinstance(specs, list) and len(specs) > 0
    assert all(isinstance(s, DeviceSpec) for s in specs)


def test_all_unit_ids_unique():
    specs = build_device_specs()
    unit_ids = [s.unit_id for s in specs]
    assert len(unit_ids) == len(set(unit_ids)), "duplicate unit_id in device spec table"


def _passive_cooling_store():
    """Compressor off (min target 0) with the passive cooling flag set."""
    calc = [0] * 300
    calc[259] = 1  # LuxtronikAddress.PASSIVE_COOLING_FLAG
    calc[10], calc[11] = 180, 160  # heat supply / return, 0.1 C
    calc[19], calc[20] = 140, 120  # source in / out
    calc[233], calc[232] = 400, 50  # condensing (calc) / evaporating
    return {"READ_CALCUL": calc}


def _read(unit_id, store):
    spec = next(s for s in build_device_specs() if s.unit_id == unit_id)
    return spec.read_converter.convert(store, spec.command, spec.address, *spec.read_args)


def test_water_delta_t_updates_during_passive_cooling():
    # The pumps run during passive cooling, so heating and source delta T stay meaningful.
    store = _passive_cooling_store()
    for unit_id in (63, 102):
        result, reason = _read(unit_id, store)
        assert result is not None and reason is None, unit_id


def test_refrigerant_deltas_stay_gated_during_passive_cooling():
    # The compressor is off during passive cooling, so refrigerant lift and
    # condensing-supply delta T describe a stopped circuit and must not be logged.
    store = _passive_cooling_store()
    for unit_id in (171, 172):
        result, reason = _read(unit_id, store)
        assert result is None and reason is not None, unit_id
