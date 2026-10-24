import pytest

from addresses import ConfigLimits
from plugin_config import PUMP_PRESETS, PluginConfig, carry_over_notice, read_plugin_config

# Domoticz always passes Mode1..Mode6; under the named-settings manifest they stay empty.
_EMPTY_MODES = {f"Mode{n}": "" for n in range(1, 7)}


def _named(**overrides):
    return {
        **_EMPTY_MODES,
        "Address": "10.0.0.5",
        "Port": "8889",
        "Version": "2.3.0",
        "Language": "en",
        "MaxCop": "45",
        "UpdateInterval": "15",
        "DeviceLanguage": "pl",
        "PumpCompensation": "custom",
        "HupMinW": "3",
        "HupMaxW": "70",
        "VboMinW": "4",
        "VboMaxW": "150",
        "UpdateCheck": "beta",
        "DebugLevel": "2",
        **overrides,
    }


def test_named_settings():
    cfg = read_plugin_config(_named())
    assert cfg == PluginConfig(
        debug_level=2,
        language="pl",
        address="10.0.0.5",
        port=8889,
        heartbeat_raw=15,
        max_cop_raw="45",
        pump_compensation="custom",
        pump_ranges_raw=("3", "70", "4", "150"),
        update_check="beta",
        plugin_version="2.3.0",
        from_legacy_fields=False,
    )
    assert cfg.pump_comp_enabled is True


def test_named_defaults_when_missing():
    cfg = read_plugin_config({**_EMPTY_MODES, "Address": "1.2.3.4", "Port": "8889"})
    assert cfg.debug_level == 0
    assert cfg.language == "en"
    assert cfg.heartbeat_raw == ConfigLimits.HEARTBEAT_DEFAULT
    assert cfg.max_cop_raw == "30"
    assert cfg.pump_compensation == "off"
    assert cfg.pump_comp_enabled is False
    assert cfg.update_check == "auto"
    assert cfg.plugin_version == ""
    assert cfg.from_legacy_fields is False


def test_named_guarded_fields_default_on_invalid():
    cfg = read_plugin_config(_named(DebugLevel="nope", UpdateInterval="x", UpdateCheck="daily"))
    assert cfg.debug_level == 0
    assert cfg.heartbeat_raw == ConfigLimits.HEARTBEAT_DEFAULT
    assert cfg.update_check == "auto"


def test_named_empty_dropdowns_use_defaults():
    cfg = read_plugin_config(
        _named(DeviceLanguage="", UpdateCheck="", DebugLevel="", PumpCompensation="")
    )
    assert cfg.language == "en"
    assert cfg.update_check == "auto"
    assert cfg.debug_level == 0
    assert cfg.pump_compensation == "off"


def test_named_empty_max_cop_stays_empty():
    # Empty is the documented way to turn the COP filter off, not a missing value.
    assert read_plugin_config(_named(MaxCop="")).max_cop_raw == ""


@pytest.mark.parametrize(
    "domoticz, expected", [("nl", "nl"), ("de", "de"), ("zh_TW", "en"), ("", "en"), ("FR", "fr")]
)
def test_language_same_as_domoticz(domoticz, expected):
    cfg = read_plugin_config(_named(DeviceLanguage="auto", Language=domoticz))
    assert cfg.language == expected


@pytest.mark.parametrize("preset", sorted(PUMP_PRESETS))
def test_pump_preset_fills_ranges(preset):
    cfg = read_plugin_config(_named(PumpCompensation=preset))
    assert cfg.pump_compensation == preset
    assert cfg.pump_ranges_raw == PUMP_PRESETS[preset]


def test_pump_presets_match_the_manual():
    assert PUMP_PRESETS == {
        "wzsv62": ("2", "60", "5", "87"),
        "wzsv92": ("2", "60", "3", "140"),
        "wzsv122": ("2", "60", "3", "180"),
        "wzsv162": ("2", "60", "3", "180"),
    }


def test_unknown_pump_choice_is_off():
    assert read_plugin_config(_named(PumpCompensation="true")).pump_comp_enabled is False


def _legacy(**overrides):
    return {
        "Address": "10.0.0.5",
        "Port": "8889",
        "Version": "2.3.0",
        "Language": "en",
        "Mode1": "45",
        "Mode2": "25",
        "Mode3": "2",
        "Mode4": "1",
        "Mode5": "3,70,4,150",
        "Mode6": "3",
        # Written by Domoticz from the manifest defaults on the first start after the upgrade.
        "MaxCop": "30",
        "UpdateInterval": "20",
        "DeviceLanguage": "auto",
        "PumpCompensation": "off",
        "UpdateCheck": "stable",
        "DebugLevel": "0",
        **overrides,
    }


def test_legacy_fields_win_until_the_hardware_page_is_saved():
    cfg = read_plugin_config(_legacy())
    assert cfg == PluginConfig(
        debug_level=3,
        language="nl",
        address="10.0.0.5",
        port=8889,
        heartbeat_raw=25,
        max_cop_raw="45",
        pump_compensation="custom",
        pump_ranges_raw=("3", "70", "4", "150"),
        update_check="stable",
        plugin_version="2.3.0",
        from_legacy_fields=True,
    )


def test_legacy_ranges_matching_a_model_select_its_preset():
    cfg = read_plugin_config(_legacy(Mode5="2, 60, 3, 140"))
    assert cfg.pump_compensation == "wzsv92"


def test_legacy_compensation_off():
    cfg = read_plugin_config(_legacy(Mode4="0"))
    assert cfg.pump_compensation == "off"


def test_legacy_unknown_language_passes_through():
    # The translator reports it and falls back to English.
    assert read_plugin_config(_legacy(Mode3="9")).language == "9"


def test_one_non_empty_legacy_field_selects_legacy():
    # A cleared Max COP (Mode1 empty) still came from the old manifest.
    cfg = read_plugin_config({**_named(), "Mode3": "0"})
    assert cfg.from_legacy_fields is True
    assert cfg.max_cop_raw == ""
    assert cfg.language == "en"


def test_legacy_guarded_fields_default_on_invalid():
    cfg = read_plugin_config(_legacy(Mode6="nope", Mode2="x"))
    assert cfg.debug_level == 0
    assert cfg.heartbeat_raw == ConfigLimits.HEARTBEAT_DEFAULT


def test_legacy_missing_language_raises():
    params = _legacy()
    del params["Mode3"]
    with pytest.raises(KeyError):
        read_plugin_config(params)


def test_missing_address_raises():
    params = _named()
    del params["Address"]
    with pytest.raises(KeyError):
        read_plugin_config(params)


def test_invalid_port_raises():
    with pytest.raises(ValueError):
        read_plugin_config(_named(Port="notaport"))


def test_carry_over_notice_lists_values_by_new_label():
    notice = carry_over_notice(read_plugin_config(_legacy()))
    assert notice is not None
    for expected in (
        "Max COP value = 45",
        "Update interval = 25 seconds (pick the nearest option)",
        "Language = Nederlands",
        "Pump power compensation = Custom: HUP min 3 W, HUP max 70 W, VBO min 4 W, VBO max 150 W",
        "Debug level = Basic + Device",
    ):
        assert expected in notice


def test_carry_over_notice_names_matching_models():
    notice = carry_over_notice(read_plugin_config(_legacy(Mode5="2,60,3,180", Mode2="20")))
    assert notice is not None
    assert "Pump power compensation = WZSV 122 or WZSV 162" in notice
    assert "Update interval = 20 seconds;" in notice


def test_carry_over_notice_flags_interval_above_the_maximum():
    notice = carry_over_notice(read_plugin_config(_legacy(Mode2="45")))
    assert notice is not None
    assert f"45 seconds (now limited to {ConfigLimits.HEARTBEAT_MAX})" in notice


def test_carry_over_notice_shows_raw_value_when_unknown():
    notice = carry_over_notice(read_plugin_config(_legacy(Mode3="9", Mode6="12", Mode4="0")))
    assert notice is not None
    assert "Language = 9" in notice
    assert "Debug level = 12" in notice
    assert "Pump power compensation = Off" in notice


def test_no_carry_over_notice_for_named_settings():
    assert carry_over_notice(read_plugin_config(_named())) is None
