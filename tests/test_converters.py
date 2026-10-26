"""Characterization tests for converters.py.

These tests lock in CURRENT behavior so future refactors are safe to verify.
They are offline-only: no DomoticzEx, no live Domoticz instance required.

All converter outputs were captured from the real implementation before being
asserted here (characterization testing, not specification testing).
"""

import pytest

import context
import converters
from addresses import ConfigLimits

# =============================================================================
# Test fixtures and helpers
# =============================================================================


HEARTBEAT_S = 20


class FakeClock:
    """Monotonic clock for the settling gate. By default every read moves time forward one
    heartbeat, so N gate checks span N heartbeats; tests that need several checks within one
    heartbeat set ``tick = 0`` and call ``advance()`` themselves."""

    def __init__(self):
        self.now = 1000.0
        self.tick = float(HEARTBEAT_S)

    def __call__(self):
        current = self.now
        self.now += self.tick
        return current

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(converters, "_monotonic", fake)
    return fake


@pytest.fixture(autouse=True)
def _ctx():
    """Inject a clean, deterministic context for every test."""
    context.logger = context._NullLogger()
    context.translator = context._PassthroughTranslator()
    context.heartbeat_interval = HEARTBEAT_S


def _steady_calls():
    """Gate checks, one per heartbeat, until SETTLING_SECONDS have elapsed since the first."""
    return ConfigLimits.SETTLING_SECONDS // HEARTBEAT_S + 1


def ds(calc):
    """Build a 300-length READ_CALCUL data store from a sparse {index: value} dict."""
    arr = [0] * 300
    for i, v in calc.items():
        arr[i] = v
    return {"READ_CALCUL": arr}


# =============================================================================
# FloatConverter
# =============================================================================


class TestFloatConverter:
    def test_divides_correctly(self):
        result = converters.FloatConverter().convert(ds({180: 792}), "READ_CALCUL", 180, 100)
        assert result == {"sValue": "7.92"}

    def test_default_divider_10(self):
        result = converters.FloatConverter().convert(ds({10: 250}), "READ_CALCUL", 10)
        assert result == {"sValue": "25.0"}

    def test_zero_value(self):
        result = converters.FloatConverter().convert(ds({10: 0}), "READ_CALCUL", 10, 10)
        assert result == {"sValue": "0.0"}

    def test_missing_index_returns_zero(self):
        # Address beyond store length -- PINNED: returns {'sValue': '0.0'} on IndexError
        result = converters.FloatConverter().convert(ds({}), "READ_CALCUL", 999, 10)
        assert result == {"sValue": "0.0"}


# =============================================================================
# NumberConverter
# =============================================================================


class TestNumberConverter:
    def test_integer_result(self):
        result = converters.NumberConverter().convert(ds({56: 3600}), "READ_CALCUL", 56, 1.0)
        assert result == {"nValue": 3600}

    def test_divider_truncates_toward_zero(self):
        # int(790 / 100) = 7 (truncates, not rounds)
        result = converters.NumberConverter().convert(ds({180: 790}), "READ_CALCUL", 180, 100)
        assert result == {"nValue": 7}

    def test_missing_index_returns_zero(self):
        # PINNED: returns {'nValue': 0} on IndexError
        result = converters.NumberConverter().convert(ds({}), "READ_CALCUL", 999)
        assert result == {"nValue": 0}


# =============================================================================
# TempDiffConverter
# =============================================================================


class TestTempDiffConverter:
    def test_positive_difference(self):
        # supply=250 (/10=25.0), return=230 (/10=23.0), diff=2.0
        result = converters.TempDiffConverter().convert(
            ds({10: 250, 11: 230}), "READ_CALCUL", [10, 11], 10
        )
        assert result == {"sValue": "2.0"}

    def test_negative_difference(self):
        # source_in=19, source_out=20: 190/10=19.0, 200/10=20.0, diff=-1.0
        result = converters.TempDiffConverter().convert(
            ds({19: 190, 20: 200}), "READ_CALCUL", [19, 20], 10
        )
        assert result == {"sValue": "-1.0"}

    def test_missing_index_returns_zero(self):
        # PINNED: returns {'sValue': '0.0'} on IndexError
        result = converters.TempDiffConverter().convert(ds({}), "READ_CALCUL", [999, 998], 10)
        assert result == {"sValue": "0.0"}


# =============================================================================
# SteadyStateGateMixin
# =============================================================================


class TestSteadyStateGateMixin:
    """The settling gate measures elapsed time since the compressor first reached its minimum
    target frequency, so it gives the same answer however many devices share one converter
    instance or how often they ask within a heartbeat."""

    def _make_mixin(self):
        """Return a fresh concrete SteadyStateGateMixin instance."""

        class _Concrete(converters.SteadyStateGateMixin, converters.DataConverter):
            def convert(self, *a, **k):
                return {}

        return _Concrete()

    # --- gate states ---

    def test_idle_when_min_freq_zero(self):
        m = self._make_mixin()
        reason = m.check_steady_state(ds({231: 50, 237: 0}))
        assert reason is not None
        assert "idle" in reason

    def test_ramping_when_actual_below_target(self):
        m = self._make_mixin()
        reason = m.check_steady_state(ds({231: 30, 237: 50}))
        assert reason is not None
        assert "ramping" in reason

    def test_settling_on_first_on_target_heartbeat(self):
        m = self._make_mixin()
        reason = m.check_steady_state(ds({231: 60, 237: 50}))
        assert reason is not None
        assert "settling" in reason

    def test_gate_passes_once_settling_seconds_elapsed(self, clock):
        m = self._make_mixin()
        store = ds({231: 60, 237: 50})
        clock.tick = 0
        assert m.check_steady_state(store) is not None  # steady from here
        clock.advance(ConfigLimits.SETTLING_SECONDS - 1)
        assert "settling" in m.check_steady_state(store)
        clock.advance(1)
        assert m.check_steady_state(store) is None

    def test_shared_instance_is_not_sped_up_by_more_devices(self, clock):
        # Several devices share one converter and each checks the gate every heartbeat.
        # The wait must still be SETTLING_SECONDS, not divided by the number of devices.
        m = self._make_mixin()
        store = ds({231: 60, 237: 50})
        clock.tick = 0
        for _ in range(ConfigLimits.SETTLING_SECONDS // HEARTBEAT_S):
            for _device in range(5):
                assert m.check_steady_state(store) is not None
            clock.advance(HEARTBEAT_S)
        assert m.check_steady_state(store) is None

    # --- resets ---

    def test_idle_restarts_the_wait(self, clock):
        m = self._make_mixin()
        store = ds({231: 60, 237: 50})
        clock.tick = 0
        m.check_steady_state(store)
        clock.advance(ConfigLimits.SETTLING_SECONDS)
        m.check_steady_state(ds({231: 0, 237: 0}))
        assert "settling" in m.check_steady_state(store)

    def test_ramping_restarts_the_wait(self, clock):
        m = self._make_mixin()
        store = ds({231: 60, 237: 50})
        clock.tick = 0
        m.check_steady_state(store)
        clock.advance(ConfigLimits.SETTLING_SECONDS)
        m.check_steady_state(ds({231: 30, 237: 50}))
        assert "settling" in m.check_steady_state(store)


# =============================================================================
# GatedFloatConverter
# =============================================================================


class TestGatedFloatConverter:
    def test_idle_returns_none_with_reason(self):
        result, reason = converters.GatedFloatConverter().convert(
            ds({231: 0, 237: 0}), "READ_CALCUL", 180, 100
        )
        assert result is None
        assert "idle" in reason

    def test_ramping_returns_none(self):
        result, reason = converters.GatedFloatConverter().convert(
            ds({231: 30, 237: 50}), "READ_CALCUL", 180, 100
        )
        assert result is None
        assert "ramping" in reason

    def test_settling_returns_none(self):
        result, reason = converters.GatedFloatConverter().convert(
            ds({231: 60, 237: 50, 180: 792}), "READ_CALCUL", 180, 100
        )
        assert result is None
        assert "settling" in reason

    def test_gate_open_returns_value_and_none_reason(self):
        """After the settling time returns ({'sValue': '7.92'}, None)."""
        c = converters.GatedFloatConverter()
        store = ds({231: 60, 237: 50, 180: 792})
        required = _steady_calls()
        for _ in range(required):
            result, reason = c.convert(store, "READ_CALCUL", 180, 100)
        assert result == {"sValue": "7.92"}
        assert reason is None

    def test_tuple_contract_both_slots_present(self):
        """Every return is a 2-tuple (result_or_None, reason_or_None)."""
        result, reason = converters.GatedFloatConverter().convert(
            ds({231: 0, 237: 0}), "READ_CALCUL", 180, 100
        )
        assert isinstance(result, (dict, type(None)))
        assert isinstance(reason, (str, type(None)))


# =============================================================================
# GatedTempDiffConverter
# =============================================================================


class TestGatedTempDiffConverter:
    def test_gated_when_idle(self):
        result, reason = converters.GatedTempDiffConverter().convert(
            ds({231: 0, 237: 0}), "READ_CALCUL", [10, 11], 10
        )
        assert result is None
        assert "idle" in reason

    def test_passive_cooling_bypasses_steady_state_gate(self):
        """PINNED: PASSIVE_COOLING_FLAG=1 bypasses the gate entirely.

        Even when compressor is idle (freq=0, min_target=0), the temp diff
        is computed and returned when passive cooling is active.
        """
        store = ds({259: 1, 231: 0, 237: 0, 10: 250, 11: 230})
        result, reason = converters.GatedTempDiffConverter().convert(
            store, "READ_CALCUL", [10, 11], 10
        )
        assert result == {"sValue": "2.0"}
        assert reason is None

    def test_gate_open_returns_diff_and_none_reason(self):
        c = converters.GatedTempDiffConverter()
        store = ds({231: 60, 237: 50, 10: 250, 11: 230})
        required = _steady_calls()
        for _ in range(required):
            result, reason = c.convert(store, "READ_CALCUL", [10, 11], 10)
        assert result == {"sValue": "2.0"}
        assert reason is None


# =============================================================================
# COPCalculatorConverter
# =============================================================================


class TestCOPCalculatorConverter:
    """COPCalculatorConverter gates on mode, passive cooling, steady-state, and noise."""

    _STEADY_STORE = None  # filled per-test by helper

    def _advance_cop_to_steady(self, c, store):
        """Advance COPCalculatorConverter c through 6 heartbeats with `store`."""
        required = _steady_calls()
        for _ in range(required):
            c.convert(store, "READ_CALCUL", 0, [257, 268])

    def test_gated_when_idle(self):
        c = converters.COPCalculatorConverter()
        result, reason = c.convert(
            ds({231: 0, 237: 0, 257: 5000, 268: 1000}),
            "READ_CALCUL",
            0,
            [257, 268],
        )
        assert result is None
        assert "idle" in reason

    def test_mode_filter_gates_before_steady_state(self):
        """Mode gate (Gate 1) fires before steady-state check."""
        c = converters.COPCalculatorConverter()
        # mode=3 (Cooling), allowed=[0, 1] -> filtered immediately, no settling needed
        store = ds({231: 60, 237: 50, 257: 5000, 268: 1000, 80: 3})
        result, reason = c.convert(store, "READ_CALCUL", 0, [257, 268, [0, 1]])
        assert result is None
        assert "mode filtered" in reason

    def test_passive_cooling_gates_after_steady_state(self):
        """Passive cooling gate (Gate 2) fires after mode check but before steady state.

        PINNED: Gate 2 check happens before Gate 3 (steady state). Even after
        the converter's counter is at 6 (gate open), a passive cooling flag
        closes it again.
        """
        c = converters.COPCalculatorConverter()
        store_run = ds({231: 60, 237: 50, 257: 5000, 268: 1000})
        self._advance_cop_to_steady(c, store_run)
        store_cooling = ds({231: 60, 237: 50, 257: 5000, 268: 1000, 259: 1})
        result, reason = c.convert(store_cooling, "READ_CALCUL", 0, [257, 268])
        assert result is None
        assert "passive cooling" in reason

    def test_valid_cop_after_settling(self):
        """PINNED: heat=5000W, power=1000W -> COP=5.00 after 6 heartbeats."""
        c = converters.COPCalculatorConverter()
        store = ds({231: 60, 237: 50, 257: 5000, 268: 1000})
        self._advance_cop_to_steady(c, store)
        result, reason = c.convert(store, "READ_CALCUL", 0, [257, 268])
        assert result == {"nValue": 0, "sValue": "5.00"}
        assert reason is None

    def test_noise_filter_blocks_low_power(self):
        """PINNED: power_input=5W < MIN_POWER_INPUT_W(10W) -> noise filter gate."""
        c = converters.COPCalculatorConverter()
        store = ds({231: 60, 237: 50, 257: 5000, 268: 5})
        self._advance_cop_to_steady(c, store)
        result, reason = c.convert(store, "READ_CALCUL", 0, [257, 268])
        assert result is None
        assert "noise filter" in reason

    def test_max_cop_gate_blocks_implausible_value(self):
        """PINNED: COP=7.0 > max_cop=6.0 -> blocked by ceiling gate."""
        c = converters.COPCalculatorConverter()
        c.max_cop = 6.0
        store = ds({231: 60, 237: 50, 257: 7000, 268: 1000})
        self._advance_cop_to_steady(c, store)
        result, reason = c.convert(store, "READ_CALCUL", 0, [257, 268])
        assert result is None
        assert "COP" in reason and "exceeds" in reason

    def test_address_arg_is_unused(self):
        """PINNED: the `address` positional arg is accepted but never read.

        Heat-output and power-input indices come entirely from config.
        Passing address=999 (out of range) has no effect.
        """
        c = converters.COPCalculatorConverter()
        store = ds({231: 60, 237: 50, 257: 5000, 268: 1000})
        self._advance_cop_to_steady(c, store)
        result, reason = c.convert(store, "READ_CALCUL", 999, [257, 268])
        assert result == {"nValue": 0, "sValue": "5.00"}
        assert reason is None


# =============================================================================
# CapacityConverter
# =============================================================================


class TestCapacityConverter:
    def _advance_cap_to_steady(self, c, store):
        required = _steady_calls()
        for _ in range(required):
            c.convert(store, "READ_CALCUL", 0, [231, 238])

    def test_max_frequency_zero_returns_none(self):
        """PINNED: max<=0 returns (None, reason) without touching the gate."""
        result, reason = converters.CapacityConverter().convert(
            ds({231: 60, 238: 0}), "READ_CALCUL", 0, [231, 238]
        )
        assert result is None
        assert "max frequency is 0" in reason

    def test_compressor_off_returns_zero_without_gate(self):
        """PINNED: actual=0 returns 0% immediately, bypassing steady-state check."""
        result, reason = converters.CapacityConverter().convert(
            ds({231: 0, 238: 120}), "READ_CALCUL", 0, [231, 238]
        )
        assert result == {"nValue": 0, "sValue": "0"}
        assert reason is None

    def test_gated_during_settling(self):
        result, reason = converters.CapacityConverter().convert(
            ds({231: 60, 237: 50, 238: 120}), "READ_CALCUL", 0, [231, 238]
        )
        assert result is None
        assert "settling" in reason

    def test_capacity_ratio_after_settling(self):
        """PINNED: actual=60, max=120 -> 50% after 6 heartbeats."""
        c = converters.CapacityConverter()
        store = ds({231: 60, 237: 50, 238: 120})
        self._advance_cap_to_steady(c, store)
        result, reason = c.convert(store, "READ_CALCUL", 0, [231, 238])
        assert result == {"nValue": 0, "sValue": "50"}
        assert reason is None

    def test_clamped_to_100_percent(self):
        """PINNED: actual=130, max=120 -> would be ~108%, clamped to 100%."""
        c = converters.CapacityConverter()
        store = ds({231: 130, 237: 50, 238: 120})
        self._advance_cap_to_steady(c, store)
        result, reason = c.convert(store, "READ_CALCUL", 0, [231, 238])
        assert result == {"nValue": 0, "sValue": "100"}
        assert reason is None


# =============================================================================
# BooleanSwitchConverter
# =============================================================================


class TestBooleanSwitchConverter:
    def test_truthy_value(self):
        result = converters.BooleanSwitchConverter().convert(ds({146: 1}), "READ_CALCUL", 146)
        assert result == {"nValue": 1, "sValue": "On"}

    def test_falsy_value(self):
        result = converters.BooleanSwitchConverter().convert(ds({146: 0}), "READ_CALCUL", 146)
        assert result == {"nValue": 0, "sValue": "Off"}

    def test_missing_index_returns_off(self):
        # PINNED: returns {'nValue': 0, 'sValue': 'Off'} on IndexError
        result = converters.BooleanSwitchConverter().convert(ds({}), "READ_CALCUL", 999)
        assert result == {"nValue": 0, "sValue": "Off"}


# =============================================================================
# IntegerValueConverter
# =============================================================================


class TestIntegerValueConverter:
    def test_integer_value(self):
        result = converters.IntegerValueConverter().convert(ds({57: 42}), "READ_CALCUL", 57)
        assert result == {"nValue": 0, "sValue": "42"}

    def test_zero_value(self):
        result = converters.IntegerValueConverter().convert(ds({57: 0}), "READ_CALCUL", 57)
        assert result == {"nValue": 0, "sValue": "0"}

    def test_missing_index_returns_zero(self):
        # PINNED: returns {'nValue': 0, 'sValue': '0'} on IndexError
        result = converters.IntegerValueConverter().convert(ds({}), "READ_CALCUL", 999)
        assert result == {"nValue": 0, "sValue": "0"}


# =============================================================================
# RuntimeHoursConverter
# =============================================================================


class TestRuntimeHoursConverter:
    def test_exact_hours(self):
        # 3600 seconds = 1 hour
        result = converters.RuntimeHoursConverter().convert(ds({56: 3600}), "READ_CALCUL", 56)
        assert result == {"nValue": 0, "sValue": "1"}

    def test_fractional_hours_rounded(self):
        # 5400 seconds = 1.5 hours -> f"{1.5:.0f}" = "2" (round-half-to-even)
        result = converters.RuntimeHoursConverter().convert(ds({56: 5400}), "READ_CALCUL", 56)
        assert result == {"nValue": 0, "sValue": "2"}

    def test_zero_seconds(self):
        result = converters.RuntimeHoursConverter().convert(ds({56: 0}), "READ_CALCUL", 56)
        assert result == {"nValue": 0, "sValue": "0"}

    def test_missing_index_returns_zero(self):
        # PINNED: returns {'nValue': 0, 'sValue': '0'} on IndexError
        result = converters.RuntimeHoursConverter().convert(ds({}), "READ_CALCUL", 999)
        assert result == {"nValue": 0, "sValue": "0"}


# =============================================================================
# TextStateConverter -- exercises translate()
# =============================================================================


class TestTextStateConverter:
    """TextStateConverter uses translate(), which calls context.translator.

    _PassthroughTranslator returns the key string unchanged, so sValue equals
    the literal key name ('Idle', 'Heating', 'DHW', 'Cooling', 'No requirement').
    """

    def test_idle_when_power_at_or_below_threshold(self):
        # power=0 <= threshold=50 -> translate('Idle')
        result = converters.TextStateConverter().convert(
            ds({80: 0, 268: 0}), "READ_CALCUL", 80, [268, 50]
        )
        assert result == {"nValue": 0, "sValue": "Idle"}

    def test_heating_mode(self):
        # mode=0 (Heating), power=1000 > 50 -> translate('Heating')
        result = converters.TextStateConverter().convert(
            ds({80: 0, 268: 1000}), "READ_CALCUL", 80, [268, 50]
        )
        assert result == {"nValue": 0, "sValue": "Heating"}

    def test_dhw_mode(self):
        # mode=1 (DHW)
        result = converters.TextStateConverter().convert(
            ds({80: 1, 268: 1000}), "READ_CALCUL", 80, [268, 50]
        )
        assert result == {"nValue": 0, "sValue": "DHW"}

    @pytest.mark.parametrize(
        "code, name",
        [
            (0, "Heating"),
            (1, "DHW"),
            (2, "Swimming pool"),
            (3, "EVU"),
            (4, "Defrost"),
            (5, "No requirement"),
            (6, "Heating ext."),
            (7, "Cooling"),
        ],
    )
    def test_controller_mode_codes(self, code, name):
        # calc[80] codes as defined by the Luxtronik protocol (python-luxtronik OperationMode).
        result = converters.TextStateConverter().convert(
            ds({80: code, 268: 1000}), "READ_CALCUL", 80, [268, 50]
        )
        assert result == {"nValue": 0, "sValue": name}

    def test_every_mode_name_is_translated(self):
        from translations import WORKING_MODE_STATUSES, Language

        for name in converters.TextStateConverter.MODE_NAMES.values():
            assert set(WORKING_MODE_STATUSES[name]) == set(Language), name

    def test_passive_cooling_flag_overrides_mode_and_power(self):
        """PINNED: PASSIVE_COOLING_FLAG=1 returns 'Cooling' regardless of power/mode.

        Even with power=0 (would normally be 'Idle'), passive cooling takes priority.
        """
        result = converters.TextStateConverter().convert(
            ds({80: 0, 268: 0, 259: 1}), "READ_CALCUL", 80, [268, 50]
        )
        assert result == {"nValue": 0, "sValue": "Cooling"}

    def test_unknown_mode_defaults_to_no_requirement(self):
        # mode=99 not in MODE_NAMES -> 'No requirement'
        result = converters.TextStateConverter().convert(
            ds({80: 99, 268: 1000}), "READ_CALCUL", 80, [268, 50]
        )
        assert result == {"nValue": 0, "sValue": "No requirement"}

    def test_translate_passthrough_with_null_translator(self):
        """PINNED: _PassthroughTranslator returns the key unchanged."""
        assert converters.translate("Heating") == "Heating"
        assert converters.translate("Idle") == "Idle"
        assert converters.translate("Cooling") == "Cooling"
        assert converters.translate("DHW") == "DHW"


# =============================================================================
# SelectorSwitchConverter
# =============================================================================


class TestSelectorSwitchConverter:
    def test_first_value_maps_to_level_0(self):
        result = converters.SelectorSwitchConverter().convert(
            ds({3: 0}), "READ_CALCUL", 3, [0, 1, 2]
        )
        assert result == {"nValue": 0, "sValue": "0"}

    def test_second_value_maps_to_level_10(self):
        result = converters.SelectorSwitchConverter().convert(
            ds({3: 1}), "READ_CALCUL", 3, [0, 1, 2]
        )
        assert result == {"nValue": 10, "sValue": "10"}

    def test_third_value_maps_to_level_20(self):
        result = converters.SelectorSwitchConverter().convert(
            ds({3: 2}), "READ_CALCUL", 3, [0, 1, 2]
        )
        assert result == {"nValue": 20, "sValue": "20"}

    def test_value_not_in_mapping_defaults_to_zero(self):
        # PINNED: unmapped value silently defaults to level 0
        result = converters.SelectorSwitchConverter().convert(
            ds({3: 99}), "READ_CALCUL", 3, [0, 1, 2]
        )
        assert result == {"nValue": 0, "sValue": "0"}


# =============================================================================
# FreqHeadroomConverter
# =============================================================================


class TestFreqHeadroomConverter:
    def test_compressor_off_returns_none(self):
        """actual=0 -> (None, 'idle (compressor off)')."""
        result, reason = converters.FreqHeadroomConverter().convert(
            ds({236: 43, 231: 0}), "READ_CALCUL", [236, 231]
        )
        assert result is None
        assert reason == "idle (compressor off)"

    def test_headroom_positive(self):
        """target=43, actual=40 -> headroom=3."""
        result, reason = converters.FreqHeadroomConverter().convert(
            ds({236: 43, 231: 40}), "READ_CALCUL", [236, 231]
        )
        assert result == {"sValue": "3"}
        assert reason is None

    def test_headroom_negative_when_above_target(self):
        """target=40, actual=43 -> headroom=-3 (running above target)."""
        result, reason = converters.FreqHeadroomConverter().convert(
            ds({236: 40, 231: 43}), "READ_CALCUL", [236, 231]
        )
        assert result == {"sValue": "-3"}
        assert reason is None

    def test_tuple_contract(self):
        """Every return is a 2-tuple (result_or_None, reason_or_None)."""
        result, reason = converters.FreqHeadroomConverter().convert(
            ds({236: 43, 231: 0}), "READ_CALCUL", [236, 231]
        )
        assert isinstance(result, (dict, type(None)))
        assert isinstance(reason, (str, type(None)))


# =============================================================================
# Write converters
# =============================================================================


class TestCommandToNumberConverter:
    def test_on_returns_one(self):
        assert converters.CommandToNumberConverter().convert(Command="On") == 1

    def test_off_returns_zero(self):
        assert converters.CommandToNumberConverter().convert(Command="Off") == 0

    def test_other_command_returns_none(self):
        # A stray command must not be read as Off; None means nothing is written.
        assert converters.CommandToNumberConverter().convert(Command="Set Level") is None

    def test_default_arg_returns_none(self):
        assert converters.CommandToNumberConverter().convert() is None


class TestLevelWithDividerConverter:
    def test_divides_level(self):
        c = converters.LevelWithDividerConverter(divider=10)
        assert c.convert(Level=100) == 10

    def test_truncates_toward_zero(self):
        # int(15 / 10) = 1 (truncates, not rounds)
        c = converters.LevelWithDividerConverter(divider=10)
        assert c.convert(Level=15) == 1

    def test_zero_level(self):
        c = converters.LevelWithDividerConverter(divider=10)
        assert c.convert(Level=0) == 0

    def test_default_level_arg_returns_zero(self):
        # Level defaults to 0
        c = converters.LevelWithDividerConverter(divider=10)
        assert c.convert() == 0


# =============================================================================
# CompressionRatioConverter (Slice 2)
# =============================================================================
class TestCompressionRatioConverter:
    def _advance(self, c, store):
        required = _steady_calls()
        for _ in range(required - 1):
            c.convert(store, "READ_CALCUL", [180, 181])

    def test_idle_gated(self):
        result, reason = converters.CompressionRatioConverter().convert(
            ds({231: 0, 237: 0}), "READ_CALCUL", [180, 181]
        )
        assert result is None and reason is not None

    def test_steady_ratio_uses_absolute(self):
        # HD 27.0 gauge, ND 5.0 gauge -> (27.0+1.013)/(5.0+1.013) = 4.66
        c = converters.CompressionRatioConverter()
        store = ds({231: 60, 237: 50, 180: 2700, 181: 500})
        self._advance(c, store)
        result, reason = c.convert(store, "READ_CALCUL", [180, 181])
        assert reason is None
        assert result == {"sValue": "4.66"}


# =============================================================================
# DischargeHeadroomConverter (Slice 2) -- steady-state gate, NO passive bypass
# =============================================================================
class TestDischargeHeadroomConverter:
    def _advance(self, c, store):
        required = _steady_calls()
        for _ in range(required - 1):
            c.convert(store, "READ_CALCUL", [252, 14], 10)

    def test_idle_gated(self):
        result, reason = converters.DischargeHeadroomConverter().convert(
            ds({231: 0, 237: 0}), "READ_CALCUL", [252, 14], 10
        )
        assert result is None and reason is not None

    def test_steady_headroom(self):
        # T-HG max 115.0 - hot gas 70.0 = 45.0 K
        c = converters.DischargeHeadroomConverter()
        store = ds({231: 60, 237: 50, 252: 1150, 14: 700})
        self._advance(c, store)
        result, reason = c.convert(store, "READ_CALCUL", [252, 14], 10)
        assert reason is None
        assert result == {"sValue": "45.0"}

    def test_no_passive_cooling_bypass(self):
        # Compressor off + passive-cooling flag set -> still gated (no bypass)
        result, reason = converters.DischargeHeadroomConverter().convert(
            ds({231: 0, 237: 0, 259: 1, 252: 1150, 14: 700}), "READ_CALCUL", [252, 14], 10
        )
        assert result is None
