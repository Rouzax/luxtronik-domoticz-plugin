"""
Luxtronik Heat Pump Controller Plugin v2 - Refactored for DomoticzEx Framework
Author: Rouzax, 2025 (Refactored)

<plugin key="luxtronikex" name="Luxtronik Heat Pump Controller v2" author="Rouzax" version="3.0.0" externallink="https://github.com/Rouzax/luxtronik-domoticz-plugin">
    <description>
        <h2>Luxtronik Heat Pump Controller Plugin</h2><br/>
        <p>This plugin connects to Luxtronik-based heat pump controllers using socket communication.</p>
        <p>Documentation, settings and troubleshooting: <a href="https://rouzax.github.io/luxtronik-domoticz-plugin/" target="_blank">rouzax.github.io/luxtronik-domoticz-plugin</a></p>

        <h3>Features:</h3>
        <ul>
            <li>Real-time monitoring of heat pump parameters</li>
            <li>Support for temperature readings, operating modes, and power consumption</li>
            <li>Multi-language support (English, Polish, Dutch, German, French)</li>
            <li>Configurable update intervals</li>
            <li>Multi-instance support for multiple heat pumps</li>
        </ul>

        <h3>Configuration Notes:</h3>
        <ul>
            <li>Requires Domoticz 2026.1 or newer</li>
            <li>Upgrading from 2.2.x or older: your previous settings stay in use until you save this page, and the fields below show defaults. Choose your values again before pressing Update; the Domoticz log and a one-time notification list them</li>
        </ul>

        <h3>Security Notes:</h3>
        <ul>
            <li>The Luxtronik protocol uses plain TCP without encryption (hardware limitation)</li>
            <li>Keep your heat pump on a trusted LAN/VLAN; do not expose to the internet</li>
            <li>Use a VPN if remote access is required</li>
        </ul>

        <h3>COP Accuracy Note:</h3>
        <p>For accurate COP averages over time, enable: <b>Settings → Log History → 'Only add newly received values to the Log'</b></p>
        <p>When disabled, Domoticz fills in the last received value every 5 minutes even when the heat pump is idle, skewing COP averages.</p>
        <p>The controller's power reading only measures compressor power. Set 'Pump power compensation' to your model to include estimated circulation pump power for true system COP.</p>
    </description>
    <params>
        <param field="Address" label="IP address" width="200px" required="true" default="127.0.0.1">
            <description>IP address of your Luxtronik heat pump controller</description>
        </param>
        <param field="Port" label="Port" width="60px" required="true" default="8889">
            <description>TCP port of the controller; 8889 unless you changed it</description>
        </param>
        <param field="DeviceLanguage" label="Language" width="160px" default="auto">
            <description>Language of device names. Names you changed yourself are kept.</description>
            <options>
                <option label="Same as Domoticz" value="auto" default="true"/>
                <option label="English" value="en"/>
                <option label="Polski" value="pl"/>
                <option label="Nederlands" value="nl"/>
                <option label="Deutsch" value="de"/>
                <option label="Français" value="fr"/>
            </options>
        </param>
        <param field="UpdateInterval" label="Update interval" width="160px" default="20">
            <description>How often the plugin reads the heat pump</description>
            <options>
                <option label="10 seconds" value="10"/>
                <option label="15 seconds" value="15"/>
                <option label="20 seconds" value="20" default="true"/>
                <option label="30 seconds" value="30"/>
            </options>
        </param>
        <param field="PumpCompensation" label="Pump power compensation" width="220px" default="off">
            <description>The controller measures compressor power only. Choose your heat pump model to add the estimated power of the heating and brine circulation pumps, for a true system COP; the values come from the WZSV manual. Choose Custom to enter the pump power ranges yourself, for another model or different pumps.</description>
            <options>
                <option label="Off" value="off" default="true"/>
                <option label="WZSV 62" value="wzsv62"/>
                <option label="WZSV 92" value="wzsv92"/>
                <option label="WZSV 122" value="wzsv122"/>
                <option label="WZSV 162" value="wzsv162"/>
                <option label="Custom" value="custom"/>
            </options>
        </param>
        <param field="HupMinW" label="Heating pump min (W)" type="number" min="0" step="1" width="75px" default="2" visible_when="PumpCompensation=custom">
        </param>
        <param field="HupMaxW" label="Heating pump max (W)" type="number" min="0" step="1" width="75px" default="60" visible_when="PumpCompensation=custom">
        </param>
        <param field="VboMinW" label="Brine pump min (W)" type="number" min="0" step="1" width="75px" default="3" visible_when="PumpCompensation=custom">
        </param>
        <param field="VboMaxW" label="Brine pump max (W)" type="number" min="0" step="1" width="75px" default="140" visible_when="PumpCompensation=custom">
        </param>
        <param field="MaxCop" label="Max COP value" type="number" min="0" step="0.1" width="75px" default="30">
            <description>COP readings above this are discarded as measurement artifacts. 0 or empty turns the filter off.</description>
        </param>
        <param field="UpdateCheck" label="Update check" width="220px" default="auto">
            <description>Once a day the plugin asks GitHub whether a newer version exists, and announces it once through the Domoticz notification systems and in the log. Automatic reports betas while you run a beta and only stable releases while you run a stable one. It sends nothing about you or your heat pump; Off stops the check.</description>
            <options>
                <option label="Automatic" value="auto" default="true"/>
                <option label="Stable releases only" value="stable"/>
                <option label="Including betas" value="beta"/>
                <option label="Off" value="off"/>
            </options>
        </param>
        <param field="DebugLevel" label="Debug level" width="220px" default="0">
            <description>None for normal use. Raise it only while troubleshooting; the higher levels fill the log quickly.</description>
            <options>
                <option label="None" value="0" default="true"/>
                <option label="Basic" value="1"/>
                <option label="Basic + Device" value="3"/>
                <option label="Basic + Comms" value="5"/>
                <option label="Basic + Device + Comms" value="7"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import datetime
import queue
from typing import Any, Dict, Optional, Tuple

import domoticz_api
import name_ownership
import update_check
from addresses import ConfigLimits, LuxtronikAddress, SocketCommand
from connection import ConnectionManager
from context import DebugLevel
from converters import COMPRESSOR_POWER_KEY, CycleTracker, DataStore
from debug_logger import DebugLogger
from device_factory import DeviceFactory
from device_spec import DeviceSpec, Field
from device_specs_table import build_device_specs
from device_update_tracker import DeviceUpdateTracker
from fault_codes import fault_message
from plugin_config import carry_over_notice, read_plugin_config
from translation_manager import TranslationManager
from translations import DEVICE_TRANSLATIONS, SELECTOR_OPTIONS, WORKING_MODE_STATUSES

# Global logger instance
_logger = DebugLogger()

# Heartbeat interval in seconds (set during onStart, used for settling time calculations)
_heartbeat_interval: int = ConfigLimits.HEARTBEAT_DEFAULT


# Global translation manager
_translator = TranslationManager()

REPOSITORY = "Rouzax/luxtronik-domoticz-plugin"


# =============================================================================
# Module-level spec storage (for command handling across restarts)
# =============================================================================
# NOTE: These globals are necessary due to DomoticzEx framework constraints.
# The framework calls Unit.onCommand() directly without passing plugin context.
# There is no clean way to inject dependencies into Unit instances at runtime,
# so we use module-level storage that is populated during plugin initialization.
# This pattern is safe because:
# 1. Domoticz runs plugin callbacks on one thread per hardware instance (the update-check
#    thread never touches these; it only posts to a queue the heartbeat drains)
# 2. The globals are only written during onStart() and cleared during onStop()
# 3. Each hardware instance has its own Python interpreter context
_unit_specs: Dict[Tuple[str, int], "DeviceSpec"] = {}  # (DeviceID, Unit) -> Spec
_plugin_ref: Optional["LuxtronikPlugin"] = None  # Reference to plugin instance


# =============================================================================
# Main Plugin Class
# =============================================================================
class LuxtronikPlugin:
    """Main plugin class orchestrating all components."""

    def __init__(self):
        self.connection: Optional[ConnectionManager] = None
        self.update_tracker = DeviceUpdateTracker()
        self.cycle_tracker = CycleTracker()  # For last cycle duration tracking
        self.available_writes: Dict[int, Field] = {}
        self._device_specs: Dict[int, DeviceSpec] = {}  # Unit ID -> Spec
        self._command_specs: Dict[str, Dict[int, DeviceSpec]] = {
            "READ_CALCUL": {},
            "READ_PARAMS": {},
        }
        self._device_id: str = ""  # Will be set during onStart
        self._pump_compensation_enabled: bool = False
        self._pump_power_ranges: Optional[Dict[str, float]] = None
        self._auto_names: dict = {}
        self._migrating: bool = False
        self._state_dirty: bool = False
        # auto_names is written only once something was claimed: its absence from the stored
        # blob is what keeps an install in the migration bootstrap (see _load_state).
        self._names_persisted: bool = False
        self._update_notified: Optional[str] = None
        # '<code>@<epoch>' of the newest controller fault already seen; None until first read.
        self._fault_seen: Optional[str] = None
        self._settings_notice_sent: bool = False
        self._plugin_version: str = ""
        self._updates: "queue.Queue[update_check.UpdateResult]" = queue.Queue()
        self._checker: Optional[update_check.UpdateChecker] = None

    def _get_device_id(self) -> str:
        """Generate stable DeviceID based on HardwareID.

        HardwareID is assigned by Domoticz when hardware is created and never
        changes, even if the hardware is renamed or IP address changes.
        This ensures device stability across configuration changes.
        """
        hw_id = _parameters().get("HardwareID", "0")
        return f"luxtronikex_hw{hw_id}"

    def _init_available_writes(self) -> None:
        """Initialize available write fields."""
        self.available_writes = {
            -1: Field(),
            LuxtronikAddress.TEMP_OFFSET: Field(
                _translator.get_device_name("temp_offset"), list(range(-50, 51, 5))
            ),
            LuxtronikAddress.HEATING_MODE: Field(
                _translator.get_device_name("heating_mode"), [0, 1, 2, 3, 4]
            ),
            LuxtronikAddress.HOT_WATER_MODE: Field(
                _translator.get_device_name("hot_water_mode"), [0, 1, 2, 3, 4]
            ),
            LuxtronikAddress.DHW_TEMP_TARGET: Field(
                _translator.get_device_name("dhw_temp_target"), list(range(300, 651, 5))
            ),
            LuxtronikAddress.COOLING_ENABLED: Field(
                _translator.get_device_name("cooling_enabled"), [0, 1]
            ),
            LuxtronikAddress.DHW_POWER_MODE: Field(
                _translator.get_device_name("dhw_power_mode"), [0, 1]
            ),
            LuxtronikAddress.ROOM_TEMP_SETPOINT: Field(
                _translator.get_device_name("room_temp_setpoint"), list(range(150, 301, 5))
            ),
        }

    def create_devices(self) -> None:
        """Create all Domoticz devices."""
        global _unit_specs, _plugin_ref

        _logger.log("Creating devices", DebugLevel.BASIC)
        self._state_dirty = False

        # Store reference to plugin for command handling
        _plugin_ref = self

        self._init_available_writes()
        specs = build_device_specs()

        # Inject CycleTracker into the last_cycle device spec
        # The last_cycle device needs stateful tracking between heartbeats
        for spec in specs:
            if spec.spec_id == "last_cycle":
                spec.read_args = (self.cycle_tracker,)
                _logger.log("Injected CycleTracker into last_cycle device", DebugLevel.VERBOSE)
                break

        # Multi-instance support: unique DeviceID per hardware
        device_id = self._device_id
        refused: list[int] = []

        for spec in specs:
            unit_id = spec.unit_id  # Use explicit unit_id, not position
            name = _translator.get_device_name(spec.spec_id)
            full_name = f"{_parameters()['Name']} - {name}"

            # Store spec in module-level storage for command handling
            _unit_specs[(device_id, unit_id)] = spec

            # Store spec for later use (device updates)
            self._device_specs[unit_id] = spec
            self._command_specs[spec.command][unit_id] = spec

            # Add description if available
            description = _translator.get_device_description(spec.spec_id)
            if description:
                spec.device_params["Description"] = description

            # Check if device exists
            k = name_ownership.key(device_id, unit_id)

            if not domoticz_api.unit_exists(_devices(), device_id, unit_id):
                # Create new unit and claim everything we just wrote. Domoticz refuses new
                # units while "Accept new devices" is off, logging only its own error.
                domoticz_api.create_unit(device_id, unit_id, full_name, spec.device_params)
                if not domoticz_api.unit_exists(_devices(), device_id, unit_id):
                    refused.append(unit_id)
                    continue
                name_ownership.claim(self._auto_names, k, "name", full_name)
                created_desc = spec.device_params.get("Description")
                if created_desc:
                    name_ownership.claim(self._auto_names, k, "description", created_desc)
                if spec.selector_options:
                    name_ownership.claim(
                        self._auto_names,
                        k,
                        "options",
                        _translator.translate_selector_options(spec.selector_options),
                    )
                self._state_dirty = True
                _logger.log(
                    f"Created device {unit_id} (spec_id={spec.spec_id}): {name}", DebugLevel.DEVICE
                )
            else:
                existing_unit = domoticz_api.get_unit(_devices(), device_id, unit_id)
                needs_options_update = False
                needs_properties_update = False

                # --- Name (provenance-owned) ---
                current_name = existing_unit.Name
                name_part = (
                    current_name.split(" - ", 1)[1] if " - " in current_name else current_name
                )
                name_heuristic = _translator.is_known_device_name(name_part, spec.spec_id)
                if name_ownership.is_owned(
                    self._auto_names, k, "name", current_name, name_heuristic, self._migrating
                ):
                    if current_name != full_name:
                        existing_unit.Name = full_name
                        needs_properties_update = True
                        _logger.log(
                            f"Device {unit_id} (spec_id={spec.spec_id}) renamed: {current_name} -> {full_name}",
                            DebugLevel.DEVICE,
                        )
                    name_ownership.claim(self._auto_names, k, "name", full_name)
                    self._state_dirty = True

                # --- Description (provenance-owned) ---
                new_description = _translator.get_device_description(spec.spec_id)
                if new_description:
                    current_description = existing_unit.Description
                    desc_heuristic = _translator.is_known_description(
                        current_description, spec.spec_id
                    )
                    if name_ownership.is_owned(
                        self._auto_names,
                        k,
                        "description",
                        current_description,
                        desc_heuristic,
                        self._migrating,
                    ):
                        if current_description != new_description:
                            existing_unit.Description = new_description
                            needs_properties_update = True
                            _logger.log(
                                f"Device {unit_id} (spec_id={spec.spec_id}) description updated",
                                DebugLevel.DEVICE,
                            )
                        name_ownership.claim(self._auto_names, k, "description", new_description)
                        self._state_dirty = True

                # --- Selector options (provenance-owned) ---
                if spec.selector_options:
                    current_options = existing_unit.Options
                    if "LevelNames" in current_options:
                        current_level_names = current_options["LevelNames"]
                        new_level_names = _translator.translate_selector_options(
                            spec.selector_options
                        )
                        current_items = current_level_names.split("|")
                        opts_heuristic = all(
                            _translator.is_known_selector_option(item, opt_key)
                            for item, opt_key in zip(
                                current_items, spec.selector_options, strict=False
                            )
                        )
                        if name_ownership.is_owned(
                            self._auto_names,
                            k,
                            "options",
                            current_level_names,
                            opts_heuristic,
                            self._migrating,
                        ):
                            if current_level_names != new_level_names:
                                existing_unit.Options = {
                                    **current_options,
                                    "LevelNames": new_level_names,
                                }
                                needs_options_update = True
                                _logger.log(
                                    f"Device {unit_id} (spec_id={spec.spec_id}) selector options updated",
                                    DebugLevel.DEVICE,
                                )
                            name_ownership.claim(self._auto_names, k, "options", new_level_names)
                            self._state_dirty = True

                if needs_properties_update or needs_options_update:
                    # DomoticzEx requires UpdateProperties=True to update Name/Description
                    # and UpdateOptions=True to update Options
                    existing_unit.Update(
                        Log=False,
                        UpdateProperties=needs_properties_update,
                        UpdateOptions=needs_options_update,
                    )
                else:
                    _logger.log(
                        f"Device {unit_id} (spec_id={spec.spec_id}) already exists: {current_name}",
                        DebugLevel.DEVICE,
                    )

        if refused:
            _logger.warning(
                f"Domoticz did not accept {len(refused)} new device(s) (units "
                f"{', '.join(map(str, refused))}). Allow new devices (Setup > Settings, or "
                "'Allow for 5 minutes' in Setup > Hardware), then restart this plugin."
            )
        _logger.log(
            f"Device creation complete: {len(specs) - len(refused)} of {len(specs)} devices",
            DebugLevel.BASIC,
        )

    def update_device(self, unit_id: int, new_values: Dict[str, Any]) -> bool:
        """Update a single device with optimized tracking.

        Returns:
            True if device was updated, False if unchanged
        """
        if unit_id not in self._device_specs:
            return False

        spec = self._device_specs[unit_id]
        device_id = self._device_id

        if not domoticz_api.unit_exists(_devices(), device_id, unit_id):
            _logger.log(f"Device {unit_id} (spec_id={spec.spec_id}) not found", DebugLevel.DEVICE)
            return False

        unit = domoticz_api.get_unit(_devices(), device_id, unit_id)
        needs_update, reason, diff = self.update_tracker.needs_update(unit, new_values)

        if needs_update:
            if "nValue" in new_values:
                unit.nValue = new_values["nValue"]
            if "sValue" in new_values:
                unit.sValue = str(new_values["sValue"])
            unit.Update(Log=True)
            _logger.log(f"Updated {spec.spec_id}: {reason} - {diff}", DebugLevel.DEVICE)
            return True
        else:
            # Log tracker decisions at VERBOSE level for debugging update issues
            _logger.log(f"{spec.spec_id}: {reason}", DebugLevel.VERBOSE)
            return False

    def update_devices(self, command: str, data_store: DataStore) -> None:
        """Update all devices for a command type using shared data store.

        Args:
            command: The command type ('READ_CALCUL', 'READ_PARAMS')
            data_store: Dict mapping all command names to their data lists
        """
        _logger.log(f"Updating devices for {command}", DebugLevel.VERBOSE)

        data_list = data_store.get(command, [])
        if not data_list:
            _logger.log(f"No data in store for {command}", DebugLevel.COMMS)
            return

        # Track update statistics
        updated_count = 0
        unchanged_count = 0
        gated_count = 0

        for unit_id, spec in self._command_specs[command].items():
            try:
                address = spec.address
                result = spec.read_converter.convert(data_store, command, address, *spec.read_args)

                # Handle both tuple (gated converters) and dict (regular converters) returns
                if isinstance(result, tuple):
                    new_values, gate_reason = result
                else:
                    new_values, gate_reason = result, None

                # Skip update if converter returns None (gating active)
                if new_values is None:
                    gated_count += 1
                    if gate_reason:
                        _logger.log(
                            f"Skipping {spec.spec_id}: gated - {gate_reason}", DebugLevel.VERBOSE
                        )
                    else:
                        _logger.log(
                            f"Skipping {spec.spec_id}: converter returned None", DebugLevel.VERBOSE
                        )
                    continue

                if self.update_device(unit_id, new_values):
                    updated_count += 1
                else:
                    unchanged_count += 1
            except Exception as e:
                _logger.error(f"Error updating device {unit_id} (spec_id={spec.spec_id})", exc=e)

        # Log summary at BASIC level
        _logger.log(
            f"{command}: Updated {updated_count}, unchanged {unchanged_count}, gated {gated_count}",
            DebugLevel.BASIC,
        )

    def update_all(self) -> None:
        """Update all devices from all sources.

        Fetches all command data first into a shared data_store, then updates
        devices. This allows gated converters to access data from other commands
        (e.g., compressor frequency from READ_CALCUL for steady-state checks).

        Uses a single TCP connection for all read commands to avoid redundant
        handshakes (the Luxtronik controller supports sequential commands).
        """
        _logger.log("Full update starting", DebugLevel.VERBOSE)

        # Command codes mapping
        command_codes = {
            "READ_CALCUL": SocketCommand.READ_CALCUL,
            "READ_PARAMS": SocketCommand.READ_PARAMS,
        }

        # Phase 1: Fetch all command data on a single connection
        batch = [(code, 0, 0) for code in command_codes.values()]
        assert self.connection is not None  # set in onStart before any update runs
        batch_results = self.connection.execute_batch_with_retry(batch)

        data_store: DataStore = {}
        for command_name, code in command_codes.items():
            result = batch_results.get(code)
            if result:
                _, _, length, data_list = result
                if length > 0:
                    data_store[command_name] = data_list
                    _logger.log(f"Fetched {command_name}: {length} values", DebugLevel.VERBOSE)
                else:
                    _logger.log(f"No data received for {command_name}", DebugLevel.COMMS)
            else:
                _logger.log(f"No result for {command_name}", DebugLevel.COMMS)

        # Apply pump power compensation (modifies POWER_TOTAL in-place)
        self._apply_pump_compensation(data_store)

        # Phase 2: Update devices with shared data store
        for command in command_codes:
            if command in data_store:
                self.update_devices(command, data_store)

        self._check_new_fault(data_store)

        _logger.log("Full update complete", DebugLevel.VERBOSE)

    def _validate_heartbeat(self, requested: int) -> int:
        """Validate and clamp heartbeat interval to safe range.

        Args:
            requested: User-requested heartbeat interval in seconds

        Returns:
            Clamped heartbeat value within ConfigLimits.HEARTBEAT_MIN and HEARTBEAT_MAX
        """
        if requested < ConfigLimits.HEARTBEAT_MIN:
            _logger.warning(
                f"Heartbeat interval {requested}s is below minimum. "
                f"Adjusted to {ConfigLimits.HEARTBEAT_MIN}s"
            )
            return ConfigLimits.HEARTBEAT_MIN
        elif requested > ConfigLimits.HEARTBEAT_MAX:
            _logger.warning(
                f"Heartbeat interval {requested}s exceeds maximum. "
                f"Adjusted to {ConfigLimits.HEARTBEAT_MAX}s"
            )
            return ConfigLimits.HEARTBEAT_MAX
        return requested

    def _configure_max_cop(self, raw_value: str) -> None:
        """Parse and apply the max COP limit to the COP converter.

        Args:
            raw_value: The Max COP setting as entered.
                       Empty string or '0' disables filtering.
                       Positive float sets the upper COP limit.
        """
        raw_value = raw_value.strip()

        if not raw_value or raw_value == "0":
            DeviceFactory._cop_converter.max_cop = None
            _logger.log("Max COP filter: disabled", DebugLevel.BASIC)
            return

        try:
            max_cop = float(raw_value)
            if max_cop <= 0:
                DeviceFactory._cop_converter.max_cop = None
                _logger.log("Max COP filter: disabled (non-positive value)", DebugLevel.BASIC)
            else:
                DeviceFactory._cop_converter.max_cop = max_cop
                _logger.log(f"Max COP filter: enabled at {max_cop:.1f}", DebugLevel.BASIC)
        except ValueError:
            DeviceFactory._cop_converter.max_cop = None
            _logger.warning(
                f"Invalid Max COP value '{raw_value}', filter disabled. Expected a positive number."
            )

    def _configure_pump_compensation(self, enabled: bool, ranges_raw: tuple[str, ...]) -> None:
        """Parse pump power compensation settings.

        Args:
            enabled: whether compensation is switched on
            ranges_raw: HUP min, HUP max, VBO min, VBO max in watts, unparsed
        """
        self._pump_compensation_enabled = enabled
        self._pump_power_ranges = None

        if not self._pump_compensation_enabled:
            return

        try:
            if len(ranges_raw) != 4:
                raise ValueError(f"expected 4 values, got {len(ranges_raw)}")
            names = ("Heating pump min", "Heating pump max", "Brine pump min", "Brine pump max")
            parts = []
            for name, raw in zip(names, ranges_raw, strict=True):
                try:
                    value = float(raw.strip())
                except ValueError:
                    raise ValueError(f"{name} '{raw.strip()}' is not a number") from None
                if value < 0:
                    raise ValueError(f"{name} {value:g} W is negative")
                parts.append(value)
            for pump, low, high in (("Heating pump", 0, 1), ("Brine pump", 2, 3)):
                if parts[low] > parts[high]:
                    raise ValueError(f"{pump} min {parts[low]:g} W is above max {parts[high]:g} W")
            self._pump_power_ranges = {
                "hup_min": parts[0],
                "hup_max": parts[1],
                "vbo_min": parts[2],
                "vbo_max": parts[3],
            }
            _logger.log(
                f"Pump power compensation enabled: HUP {parts[0]}-{parts[1]}W, VBO {parts[2]}-{parts[3]}W",
                DebugLevel.BASIC,
            )
        except (ValueError, IndexError) as e:
            _logger.error(
                f"Pump power compensation off: {e} (values '{','.join(ranges_raw)}'). "
                "Correct them on the hardware page."
            )
            self._pump_compensation_enabled = False

    @staticmethod
    def _estimate_pump_power(speed_pct: float, p_min: float, p_max: float) -> float:
        """Estimate pump power from speed percentage using quadratic model.

        Quadratic is a reasonable middle ground between linear (overestimates)
        and cubic affinity law (underestimates for ECM pumps).
        """
        if speed_pct <= 0:
            return 0.0
        fraction = max(0.0, min(1.0, speed_pct / 100.0))
        return p_min + (p_max - p_min) * fraction * fraction

    def _apply_pump_compensation(self, data_store: DataStore) -> None:
        """Add estimated pump power to compressor power reading in data store.

        Modifies POWER_TOTAL in-place so all downstream converters
        (power devices, COP calculators) automatically use the corrected value.
        """
        if not self._pump_compensation_enabled or self._pump_power_ranges is None:
            return

        calc_data = data_store.get("READ_CALCUL", [])
        if not calc_data:
            return

        try:
            ranges = self._pump_power_ranges
            compressor_power = float(calc_data[LuxtronikAddress.POWER_TOTAL])
            hup_speed = float(calc_data[LuxtronikAddress.HEATING_PUMP_SPEED])
            vbo_speed = float(calc_data[LuxtronikAddress.BRINE_PUMP_SPEED])

            hup_power = self._estimate_pump_power(hup_speed, ranges["hup_min"], ranges["hup_max"])
            vbo_power = self._estimate_pump_power(vbo_speed, ranges["vbo_min"], ranges["vbo_max"])

            total_power = compressor_power + hup_power + vbo_power
            data_store[COMPRESSOR_POWER_KEY] = [compressor_power]  # type: ignore[list-item]
            # Intentional float into the int calc list: compensated power carries
            # sub-watt precision that InstantPowerConverter reads back as a float.
            calc_data[LuxtronikAddress.POWER_TOTAL] = total_power  # type: ignore[assignment]

            _logger.log(
                f"Pump compensation: compressor={compressor_power:.0f}W + "
                f"HUP({hup_speed:.0f}%)={hup_power:.0f}W + "
                f"VBO({vbo_speed:.0f}%)={vbo_power:.0f}W = {total_power:.0f}W",
                DebugLevel.DEVICE,
            )
        except (IndexError, TypeError, ValueError) as e:
            _logger.log(f"Pump compensation error: {type(e).__name__}: {e}", DebugLevel.VERBOSE)

    def _check_cop_logging_setting(self) -> None:
        """Check and warn if COP logging setting is not optimal.

        For accurate COP averages over time, Domoticz should be configured with:
        Settings → Log History → 'Only add newly received values to the Log' = ENABLED

        When disabled (default), Domoticz fills in the last received value every 5 minutes,
        even when no new data is received. This means if the last COP sent was 10.2, that
        value gets logged every 5 minutes even when the heat pump is idle, skewing averages.

        When enabled, Domoticz only logs values when they are actually received, creating
        gaps during idle periods. This gives accurate daily/monthly COP averages.
        """
        settings = _settings()
        if settings is None:
            # Settings dictionary not available (older Domoticz version?)
            _logger.log(
                "Settings dictionary not available, skipping COP logging check", DebugLevel.VERBOSE
            )
            return

        try:
            # Settings dictionary is populated by Domoticz plugin framework
            # ShortLogAddOnlyNewValues: 1 = enabled (recommended), 0 = disabled
            # Note: Settings values are returned as strings
            setting_value = settings.get("ShortLogAddOnlyNewValues", "0")

            # Handle string comparison (Settings returns strings)
            if str(setting_value) == "1":
                _logger.log(
                    "COP Logging: 'Only add newly received values' is ENABLED (recommended)",
                    DebugLevel.BASIC,
                )
            else:
                # This is an important warning, always show it
                domoticz_api.log_status(
                    "COP Warning: For accurate COP averages, enable "
                    "Settings → Log History → 'Only add newly received values to the Log'. "
                    "Currently disabled - stale values will be logged during idle periods."
                )
        except Exception as e:
            # Other errors - log but don't fail
            _logger.log(f"Could not check COP logging setting: {e}", DebugLevel.VERBOSE)

    def onStart(self) -> None:
        """Initialize the plugin."""
        global _logger, _translator, _heartbeat_interval

        try:
            cfg = read_plugin_config(_parameters())
            self._plugin_version = cfg.plugin_version

            # Setup debugging
            _logger.level = cfg.debug_level
            if _logger.level == DebugLevel.NONE:
                domoticz_api.set_debugging(0)  # Silence everything
            elif _logger.level == DebugLevel.ALL:
                domoticz_api.set_debugging(62)  # Plugin Debug() + framework device/connection info
            else:
                domoticz_api.set_debugging(2)  # Only plugin Debug() calls, no framework noise

            _logger.log("Plugin starting", DebugLevel.BASIC)

            # Bridge live logger/translator into context so extracted modules
            # (including TranslationManager.set_language below) can log through
            # the real logger instead of the pre-onStart null logger.
            import context

            context.logger = _logger
            context.translator = _translator

            # Initialize translations
            _translator.load_translations(
                DEVICE_TRANSLATIONS, SELECTOR_OPTIONS, WORKING_MODE_STATUSES
            )
            _translator.set_language(cfg.language)

            # Note: command handling is wired via the module-level onCommand()
            # function (see bottom of module). DomoticzEx dispatches commands to
            # Unit, then Device, then the module, so no custom class registration
            # is needed and it works reliably across plugin hot-reloads.

            # Generate unique DeviceID for multi-instance support
            self._device_id = self._get_device_id()
            _logger.log(f"DeviceID: {self._device_id}", DebugLevel.BASIC)

            # Initialize connection
            self.connection = ConnectionManager(cfg.address, cfg.port)

            # Set heartbeat with validation
            heartbeat = self._validate_heartbeat(cfg.heartbeat_raw)
            domoticz_api.set_heartbeat(heartbeat)
            _heartbeat_interval = heartbeat
            _logger.log(f"Heartbeat set to {heartbeat}s", DebugLevel.BASIC)

            # Bridge the computed heartbeat into context now that it's known.
            context.heartbeat_interval = _heartbeat_interval

            # Configure max COP limit
            self._configure_max_cop(cfg.max_cop_raw)
            self._configure_pump_compensation(cfg.pump_comp_enabled, cfg.pump_ranges_raw)

            # Create devices (this also initializes available_writes)
            self._load_state()
            self._announce_carry_over(carry_over_notice(cfg))
            self.create_devices()
            # Persist provenance only when something was claimed or changed this run.
            # An install whose devices are all user-renamed claims nothing, leaves
            # _state_dirty False, writes no auto_names, and stays migrating on the next
            # onStart -- a harmless no-op, since there is nothing owned to reconcile.
            if self._state_dirty:
                self._names_persisted = True
                self._persist()

            # Enable writes only for known safe addresses
            # These are the ONLY addresses that can be written to
            allowed_write_addresses = [addr for addr in self.available_writes if addr != -1]
            self.connection.enable_writes(allowed_write_addresses)
            _logger.log(
                f"Write protection enabled for {len(allowed_write_addresses)} addresses",
                DebugLevel.BASIC,
            )

            self._start_update_check(cfg.update_check)

            # Initial update
            self.update_all()

            _logger.log("Plugin started successfully", DebugLevel.BASIC)

            # Check COP logging configuration
            # Settings dictionary is populated by Domoticz plugin framework
            self._check_cop_logging_setting()

        except ValueError as e:
            _logger.error("Configuration error during plugin start", exc=e)
        except Exception as e:
            _logger.error("Plugin start failed", exc=e)

    def onStop(self) -> None:
        """Clean up plugin resources."""
        global _plugin_ref, _unit_specs

        _logger.log("Plugin stopping", DebugLevel.BASIC)

        # Not joined: a daemon thread, and a check in flight may take its full timeout.
        if self._checker is not None:
            self._checker.stop()
            self._checker = None

        if self.connection:
            # Disable writes before closing
            self.connection.disable_writes()
            self.connection.close()

        # Clear specs first so any late onCommand() won't find a spec and exits early,
        # rather than finding a spec but having no plugin reference to execute against.
        _unit_specs.clear()
        _plugin_ref = None

        _logger.log("Plugin stopped", DebugLevel.BASIC)

    def onHeartbeat(self) -> None:
        """Handle periodic updates."""
        _logger.log("Heartbeat triggered", DebugLevel.VERBOSE)
        # Own guard: a failed announcement must not skip reading the heat pump.
        try:
            self._announce_updates()
        except Exception as e:
            _logger.error("Update announcement failed", exc=e)
        self.update_all()

    def _load_state(self) -> None:
        blob = domoticz_api.load_state() or {}
        # Migrating is keyed on auto_names, not on the blob existing: the update check also
        # stores state, which must not end the bootstrap for an install that has claimed
        # nothing yet.
        self._names_persisted = "auto_names" in blob
        self._migrating = not self._names_persisted
        self._auto_names = blob.get("auto_names", {})
        self._update_notified = blob.get("update_notified")
        self._fault_seen = blob.get("fault_seen")
        self._settings_notice_sent = bool(blob.get("settings_notice_sent"))

    def _persist(self) -> None:
        """Store the plugin state blob. Domoticz replaces the whole blob on every write, so
        each write carries every key."""
        state: Dict[str, Any] = {"v": 1}
        if self._names_persisted:
            state["auto_names"] = self._auto_names
        if self._update_notified:
            state["update_notified"] = self._update_notified
        if self._fault_seen:
            state["fault_seen"] = self._fault_seen
        if self._settings_notice_sent:
            state["settings_notice_sent"] = True
        domoticz_api.save_state(state)

    def _announce_carry_over(self, notice: Optional[str]) -> None:
        """Log the carry-over notice at every start, and notify once: saving the hardware page
        unread resets the values, and many users never open the log."""
        if not notice:
            return
        domoticz_api.log_status(notice)
        if self._settings_notice_sent:
            return
        domoticz_api.send_notification(
            "Luxtronik plugin: check your settings before saving", notice
        )
        self._settings_notice_sent = True
        self._persist()

    def _start_update_check(self, channel: str) -> None:
        # Domoticz passes the manifest version; without it there is nothing to compare against.
        if channel == "off" or not self._plugin_version:
            return
        self._checker = update_check.UpdateChecker(
            REPOSITORY,
            self._plugin_version,
            channel,
            self._updates,
            user_agent=f"luxtronikex/{self._plugin_version} update-check",
        )
        self._checker.start()

    def _check_new_fault(self, data_store: DataStore) -> None:
        """Announce a fault the controller stored since the last check: one error line and one
        notification. The fault present the first time the plugin reads the controller is
        only recorded, so installing or upgrading does not announce an old fault."""
        calc = data_store.get("READ_CALCUL", [])
        try:
            code = int(calc[LuxtronikAddress.ERROR_CODE_LATEST])
            stamp = int(calc[LuxtronikAddress.ERROR_TIME_LATEST])
        except (IndexError, TypeError, ValueError):
            return
        if code <= 0:
            return
        seen = f"{code}@{stamp}"
        if seen == self._fault_seen:
            return
        first_read = self._fault_seen is None
        self._fault_seen = seen
        self._persist()
        if first_read:
            return
        message = fault_message(code, _translator.language) or "Unknown fault"
        when = datetime.datetime.fromtimestamp(stamp).strftime("%Y-%m-%d %H:%M") if stamp else ""
        _logger.error(f"Heat pump fault {code}: {message} ({when})")
        domoticz_api.send_notification(
            f"Heat pump fault {code}: {message}",
            f"The heat pump controller reported fault {code} ({message}) at {when}.",
        )

    def _announce_updates(self) -> None:
        """Announce each newer version once: a log line and one notification through every
        notification system Domoticz has (an empty subsystem)."""
        while True:
            try:
                result = self._updates.get_nowait()
            except queue.Empty:
                return
            if result.error:
                _logger.log(f"Update check failed: {result.error}", DebugLevel.COMMS)
                continue
            if result.version is None or result.version == self._update_notified:
                continue
            domoticz_api.log_status(
                f"Update available: version {result.version} (running {self._plugin_version}). "
                f"Release notes and download: {result.url}"
            )
            domoticz_api.send_notification(
                f"Luxtronik plugin {result.version} is available",
                f"Version {result.version} of the Luxtronik heat pump plugin is available; "
                f"you run {self._plugin_version}. {result.url}",
            )
            self._update_notified = result.version
            self._persist()


# =============================================================================
# Plugin Instance and Callbacks
# =============================================================================


def _devices():
    """The framework-injected Devices mapping (None before onStart)."""
    return globals().get("Devices")


def _parameters() -> dict:
    """The framework-injected Parameters mapping (empty before onStart)."""
    return globals().get("Parameters") or {}


def _settings():
    """The framework-injected Settings mapping (None if unavailable)."""
    return globals().get("Settings")


_plugin = LuxtronikPlugin()


def onStart():
    try:
        _plugin.onStart()
    except Exception as e:
        domoticz_api.log_error(f"onStart failed ({type(e).__name__}: {e})")


def onStop():
    try:
        _plugin.onStop()
    except Exception as e:
        domoticz_api.log_error(f"onStop failed ({type(e).__name__}: {e})")


def onHeartbeat():
    try:
        _plugin.onHeartbeat()
    except Exception as e:
        domoticz_api.log_error(f"onHeartbeat failed ({type(e).__name__}: {e})")


def onCommand(DeviceID: str, Unit: int, Command: str, Level: int, Color: str) -> None:
    """Handle a command sent to one of the plugin's units.

    DomoticzEx dispatches commands to the Unit object, then the Device object,
    then this module-level function, in that order. Because the plugin uses the
    base DomoticzEx.Unit/Device classes (no custom subclass registration), the
    dispatch always falls through to here, which works reliably across plugin
    hot-reloads.

    SAFETY: All writes are validated against available_writes before sending to
    protect the heat pump's EEPROM from invalid values.
    """
    try:
        global _unit_specs, _plugin_ref

        spec = _unit_specs.get((DeviceID, Unit))

        if spec:
            _logger.log(
                f"Command received: spec_id={spec.spec_id}, Unit={Unit}, Command={Command}, Level={Level}",
                DebugLevel.COMMS,
            )
        else:
            _logger.log(
                f"Command received: DeviceID={DeviceID}, Unit={Unit}, Command={Command}, Level={Level}",
                DebugLevel.COMMS,
            )

        if not spec or not spec.write_converter or not _plugin_ref:
            _logger.log(f"No write handler for unit {Unit}", DebugLevel.COMMS)
            return

        try:
            # Convert command to value (Color is DomoticzEx's Hue payload)
            value = spec.write_converter.convert(
                Command=Command,
                Level=Level,
                Hue=Color,
                available_writes=_plugin_ref.available_writes,
            )

            if value is None:
                _logger.error(
                    f"WRITE BLOCKED: command '{Command}' (level {Level}) is not a valid option "
                    f"(spec_id={spec.spec_id})"
                )
                return

            # Get address from spec
            address = spec.address
            if isinstance(address, list):
                address = address[0]

            # CRITICAL SAFETY CHECK: Validate value against allowed writes
            # This protects the heat pump's EEPROM from invalid values
            if address not in _plugin_ref.available_writes:
                _logger.error(
                    f"WRITE BLOCKED: Address {address} not in available_writes (spec_id={spec.spec_id})"
                )
                return

            allowed_values = _plugin_ref.available_writes[address].get_val()
            if value not in allowed_values:
                _logger.error(
                    f"WRITE BLOCKED: Invalid value {value} for "
                    f"{_plugin_ref.available_writes[address].get_name()} (spec_id={spec.spec_id}). "
                    f"Allowed values: {allowed_values}"
                )
                return

            _logger.log(
                f"Writing validated value {value} to address {address} (spec_id={spec.spec_id})",
                DebugLevel.BASIC,
            )

            # Execute write command
            assert _plugin_ref.connection is not None  # set in onStart before commands dispatch
            _plugin_ref.connection.execute_with_retry(SocketCommand.WRITE_PARAMS, address, value)

            # Update all devices to reflect the change
            _plugin_ref.update_all()

        except Exception as e:
            _logger.error(f"Error processing command for spec_id={spec.spec_id}", exc=e)
    except Exception as e:
        domoticz_api.log_error(f"onCommand failed ({type(e).__name__}: {e})")
