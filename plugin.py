# Luxtronik plugin based on sockets
# Author: ajarzyna, Rouzax, 2025
"""
<plugin key="luxtronik" name="Luxtronik Heat Pump Controller" author="Rouzax" version="1.0.1">
    <description>
        <h2>Luxtronik Heat Pump Controller Plugin</h2><br/>
        <p>This plugin connects to Luxtronik-based heat pump controllers using socket communication.</p>
        
        <h3>Features:</h3>
        <ul>
            <li>Real-time monitoring of heat pump parameters</li>
            <li>Support for temperature readings, operating modes, and power consumption</li>
            <li>Multi-language support (English, Polish, Dutch)</li>
            <li>Configurable update intervals</li>
        </ul>
        
        <h3>Configuration Notes:</h3>
        <ul>
            <li>Default port for Luxtronik is typically 8889</li>
            <li>Recommended update interval: 15-30 seconds</li>
            <li>Values greater than 30 seconds will trigger a Domoticz timeout warning, but the plugin will continue to function correctly</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="Heat Pump IP Address" width="200px" required="true" default="127.0.0.1">
            <description>IP address of your Luxtronik controller</description>
        </param>
        <param field="Port" label="Heat Pump Port" width="60px" required="true" default="8889">
            <description>TCP port of your Luxtronik controller (default: 8889)</description>
        </param>
        <param field="Mode2" label="Update Interval" width="150px" required="true" default="20">
            <description>Data update interval in seconds (recommended: 15-30)</description>
        </param>
        <param field="Mode3" label="Language" width="150px">
            <description>Select interface language</description>
            <options>
                <option label="English" value="0" default="true"/>
                <option label="Polish" value="1"/>
                <option label="Dutch" value="2"/>
            </options>
        </param>
        <param field="Mode6" label="Debug Level" width="150px">
            <description>Select debug categories to enable</description>
            <options>
                <option label="None" value="0" default="true"/>
                <option label="Basic" value="1"/>
                <option label="Basic + Device" value="3"/>
                <option label="Basic + Connection" value="5"/>
                <option label="Basic + Protocol" value="9"/>
                <option label="Basic + Data Processing" value="17"/> 
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import socket
import struct
import re
import time
import errno
from translations import Language, TRANSLATIONS
from typing import Dict, List, Optional
from enum import Enum, auto

# Debug level constants
DEBUG_NONE = 0                   # 0000 0000 - No debugging
DEBUG_BASIC = 1                  # 0000 0001 - Basic plugin operations (startup, device creation, etc.)
DEBUG_DEVICE = 2                 # 0000 0010 - Device updates and state changes
DEBUG_CONN = 4                   # 0000 0100 - Connection handling
DEBUG_PROTO = 8                  # 0000 1000 - Protocol/message details
DEBUG_DATA = 16                  # 0001 0000 - Data parsing and processing
DEBUG_ALL = -1                   # 1111 1111 - All debugging enabled

# Device range mappings for descriptions
DEVICE_RANGE_MAPPINGS = {
    'Superheat': 'superheat',
    'High pressure': 'pressure_high',
    'Low pressure': 'pressure_low',
    'Hot gas temp': 'hot_gas',
    'COP total': 'cop',
    'Heating pump speed': 'pump_speed',
    'Brine pump speed': 'pump_speed',
    'Brine temp diff': 'brine_temp_diff',
    'Heating temp diff': 'heating_temp_diff',
}

# Socket command codes for communication with Luxtronik controller
# Each command represents a different type of request to the heat pump
SOCKET_COMMANDS = {
    'WRIT_PARAMS': 3002,  # Write parameters to the controller
    'READ_PARAMS': 3003,  # Read parameter values
    'READ_CALCUL': 3004,  # Read calculated values
    'READ_VISIBI': 3005   # Read visibility settings
}

def log_debug(message, level, current_debug_level):
    """
    Log debug messages based on debug level using appropriate Domoticz log levels:
    - Status: Normal operational messages (blue)
    - Debug: Detailed debug information (grey)
    - Error: Errors and exceptions (red)
    """
    try:
        if current_debug_level == DEBUG_NONE:
            return
            
        # If DEBUG_ALL is set, log everything as Debug
        if current_debug_level == DEBUG_ALL:
            Domoticz.Debug(f"[ALL] {message}")
            return
            
        # Handle specific debug levels with different Domoticz log types
        if level == DEBUG_BASIC and (current_debug_level & DEBUG_BASIC):
            # Basic info goes to Status (blue) for better visibility
            Domoticz.Status(f"[BASIC]  {message}")
            
        elif level == DEBUG_DEVICE and (current_debug_level & DEBUG_DEVICE):
            # Device updates go to Status (blue) as they're important operational info
            Domoticz.Status(f"[DEVICE] {message}")
            
        elif level == DEBUG_CONN and (current_debug_level & DEBUG_CONN):
            # Connection info goes to Debug (grey) as it's more technical
            Domoticz.Debug(f"[CONN]   {message}")
            
        elif level == DEBUG_PROTO and (current_debug_level & DEBUG_PROTO):
            # Protocol details go to Debug (grey) as they're technical details
            Domoticz.Debug(f"[PROTO]  {message}")
            
        elif level == DEBUG_DATA and (current_debug_level & DEBUG_DATA):
            # Data processing goes to Debug (grey) as it's technical detail
            Domoticz.Debug(f"[DATA]   {message}")
            
    except Exception as e:
        # Fallback logging if something goes wrong - use Error level for visibility
        Domoticz.Error(f"[INIT] {message} (Logging error: {str(e)})")
        

class DeviceUpdateTracker:
    def __init__(self):
        self.last_update_times = {}
        self.graph_update_interval = 300  # 5 minutes in seconds
        self.device_types = {}

        self.type_mapping = {
            80: ('Temperature', True),
            243: ('Custom', True),
            242: ('Custom', True),
            244: ('Switch', False)
        }

    def _check_device_type(self, device) -> bool:
        """Get cached device type information or check and cache if not present.
        
        For Text devices (which typically have Type 243 and SubType 19), mark as non-graphing.
        """
        try:
            device_id = device.ID
            
            # If the device is a Text device, mark it as non-graphing and return immediately.
            if hasattr(device, 'SubType') and device.Type == 243 and device.SubType == 19:
                self.device_types[device_id] = False
                return False
            
            if device_id not in self.device_types:
                # Look up the device type in our mapping.
                device_info = self.type_mapping.get(device.Type, ('Unknown', False))
                type_name, is_graphing = device_info
                
                if _plugin.debug_level & DEBUG_DEVICE:
                    type_info = f"Device {device_id} ({device.Name}) - Type: {device.Type} ({type_name})"
                    if is_graphing:
                        type_info += " [Graphing device]"
                    log_debug(type_info, DEBUG_DEVICE, _plugin.debug_level)
                
                self.device_types[device_id] = is_graphing
                
            return self.device_types[device_id]
            
        except Exception as e:
            log_debug(f"Error checking device type {device.Name}: {str(e)}", DEBUG_DEVICE, _plugin.debug_level)
            return False


    def _normalize_value(self, value_str: str) -> str:
        """
        Normalize a value for comparison.
        - If the value is numeric (or contains a numeric portion), return its float value formatted to one decimal.
        - Otherwise, return the trimmed (and lowercased) text for consistent text comparisons.
        """
        if not value_str:
            return ""
        
        # Trim whitespace and use only the first part if a ';' is present.
        value_str = value_str.strip()
        if ';' in value_str:
            value_str = value_str.split(';')[0].strip()
        
        try:
            return f"{float(value_str):.1f}"
        except ValueError:
            return value_str.lower()

    def needs_update(self, device, new_values) -> tuple[bool, str, str]:
        """
        Determine if a device needs an update based on its type and new values.
        Returns a tuple of:
        (needs_update, update_reason, diff_message)
        where diff_message details any numeric or text differences.
        """
        try:
            current_time = time.time()
            device_id = device.ID
            is_graphing = self._check_device_type(device)
            
            # Get current values from the device.
            current_values = {
                'nValue': device.nValue,
                'sValue': str(device.sValue)
            }
            
            values_changed = False
            diff_message = ""
            
            # Compare numeric value (nValue) directly.
            if 'nValue' in new_values and new_values['nValue'] != current_values['nValue']:
                values_changed = True
                diff_message += f"nValue: {current_values['nValue']} -> {new_values['nValue']}; "
            
            # Compare sValue using normalized comparison.
            if 'sValue' in new_values:
                norm_current = self._normalize_value(current_values['sValue'])
                norm_new = self._normalize_value(new_values['sValue'])
                if norm_current != norm_new:
                    values_changed = True
                    diff_message += (f"sValue: {current_values['sValue']} (normalized: {norm_current}) -> "
                                    f"{new_values['sValue']} (normalized: {norm_new})")
                    # (Removed extra logging here to avoid duplicate output)
            
            if values_changed:
                if is_graphing:
                    self.last_update_times[device_id] = current_time
                return True, "Values changed", diff_message
                        
            # For graphing devices, force an update after the interval even if values are equal.
            if is_graphing:
                last_update = self.last_update_times.get(device_id, 0)
                time_since_update = current_time - last_update
                if time_since_update >= self.graph_update_interval:
                    self.last_update_times[device_id] = current_time
                    return True, "Interval update", ""
                else:
                    time_until_update = self.graph_update_interval - time_since_update
                    return False, f"No changes, next update in {int(time_until_update)}s", ""
            else:
                return False, "Non-graphing device, no changes", ""
                        
        except Exception as e:
            log_debug(f"Failed to check update for {device.Name}: {str(e)}", DEBUG_DEVICE, _plugin.debug_level)
            return False, f"Error: {str(e)}", ""


# Read callbacks
def to_float(data_list: list, data_idx: int, divider: float) -> dict:
    """Convert data to float with divider"""
    converted = float(data_list[data_idx] / divider)
    return {'sValue': str(converted)}


def to_number(data_list: list, data_idx: int, divider: float = 1.0) -> dict:
    """Convert data to number with optional divider"""
    converted = float(data_list[data_idx] / divider)
    return {'nValue': int(converted)}


def selector_switch_level_mapping(data_list: list, data_idx: int, mapping: list) -> dict:
    """Map data to selector switch levels"""
    level = mapping.index(data_list[data_idx]) * 10
    return {'nValue': int(level), 'sValue': str(level)}
    
    
def to_instant_power(data_list: list, power_data_idx: int, *_args) -> dict:
    """Converts instant power to string for Computed energy meter.
    
    Args:
        data_list: List of heat pump data values
        power_data_idx: Index of power value in data_list
    Returns:
        dict: Device update parameters with instant power value
    """
    try:
        # Handle case where power_data_idx is a list
        if isinstance(power_data_idx, list):
            power_data_idx = power_data_idx[0]
            
        instant_power = float(data_list[power_data_idx])
        return {'sValue': f"{instant_power:.1f}"}
        
    except Exception as e:
        log_debug(f"Error in to_instant_power: {str(e)}", DEBUG_DATA, _plugin.debug_level)
        return {'sValue': "0.0"}

def to_instant_power_split(data_list: list, power_data_idx: int, additional_data: list, *_args) -> dict:
    """Splits instant power into heating or hot water based on operating mode.
    
    Args:
        data_list: List of heat pump data values
        power_data_idx: Index of power value in data_list
        additional_data: List containing [state_idx, valid_states]
    Returns:
        dict: Device update parameters with power value based on operating mode
    """
    try:
        state_idx, valid_states = additional_data
        
        # Handle case where power_data_idx is a list 
        if isinstance(power_data_idx, list):
            power_data_idx = power_data_idx[0]
            
        instant_power = float(data_list[power_data_idx])
        current_state = int(data_list[state_idx])
        
        # Return power value based on state
        power = instant_power if current_state in valid_states else 0.0
        return {'sValue': f"{power:.1f}"}
        
    except Exception as e:
        log_debug(f"Error in to_instant_power_split: {str(e)}", DEBUG_DATA, _plugin.debug_level)
        return {'sValue': "0.0"}

def to_cop_calculator(data_list: list, indices: int, *args) -> dict:
    """Calculates COP based on heat output and power input."""
    indices_list = args[0]
    heat_output_idx, power_input_idx = indices_list
    
    heat_output = float(data_list[heat_output_idx])
    power_input = float(data_list[power_input_idx])
    
    if power_input > 0:
        cop = heat_output / power_input
    else:
        cop = 0
    return {'sValue': str(round(cop, 2))}

def to_text_state(data_list: list, data_idx: int, config: list) -> dict:
    """
    Converts heat pump state to text status
    
    Args:
        data_list: List of data values
        data_idx: Index of the mode value in data_list
        config: List containing [power_idx, power_threshold]
        
    Returns:
        dict: Device update parameters with translated status text
    """
    # Operating modes based on ID_WEB_WP_BZ_akt values
    mode_names = {
        0: translate('Heating mode'),
        1: translate('Hot water mode'),
        2: translate('Swimming pool mode / Photovoltaik'),
        3: translate('Cooling'),
        4: translate('No requirement')
    }
    
    power_idx, power_threshold = config
    
    # Get current power consumption
    current_power = float(data_list[power_idx])
    
    # Get current mode
    current_mode = data_list[data_idx]
  
    # If power consumption is below threshold, return "No requirement"
    if current_power <= power_threshold:
        return {'nValue': 0, 'sValue': translate('No requirement')}
    
    # Map mode to text
    state_text = mode_names.get(current_mode, translate('No requirement'))
    return {'nValue': 0, 'sValue': state_text}

def calculate_temp_diff(data_list: list, indices: list, divider: float) -> dict:
    """Calculate temperature difference between two sensors
    Args:
        data_list: List of all sensor data
        indices: List containing [temp1_idx, temp2_idx]
        divider: Value to divide readings by (typically 10)
    Returns:
        dict with calculated difference
    """
    # Get temperatures and divide by the divider
    temp1 = float(data_list[indices[0]]) / divider
    temp2 = float(data_list[indices[1]]) / divider
    
    # Calculate absolute difference
    diff = abs(temp1 - temp2)
    
    # Return formatted result
    return {'sValue': str(round(diff, 1))}

# Write callbacks
def command_to_number(*_args, Command: str, **_kwargs):
    """Converts command to number."""
    return 1 if Command == 'On' else 0


def available_writes_level_with_divider(write_data_list: list, *_args,
                                        available_writes, Level, **_kwargs):
    """Returns available writes based on level and divider."""
    divider, available_writes_idx = write_data_list
    return available_writes[available_writes_idx].get_val()[int(Level / divider)]


def level_with_divider(divider: float, *_args, Level, **_kwargs):
    """Returns level divided by divider."""	
    return int(Level / divider)


class Field:
    def __init__(self, *args, **kwargs):
        if len(args) == len(kwargs) == 0:
            self.name = 'Unknown'
            self.vales = []
        else:
            self.name, self.vales = args

    def get_name(self):
        return self.name

    def get_val(self):
        return self.vales
    
class TranslationManager:
    """Manages translations for the plugin"""
    
    def __init__(self, default_language: Language = Language.ENGLISH):
        self._default_language = default_language
        self._current_language = default_language
        self._translations: Dict[str, Dict[Language, str]] = {}
        self._ranges: Dict[str, Dict[Language, Dict[str, str]]] = {}
        
    def set_language(self, language: Language) -> None:
        """Set the current language"""
        if not isinstance(language, Language):
            raise ValueError(f"Invalid language type: {type(language)}. Expected Language enum.")
        self._current_language = language
        
    def add_translation(self, key: str, translations: Dict[Language, str]) -> None:
        """Add a translation entry"""
        if not isinstance(key, str):
            raise ValueError(f"Translation key must be string, got {type(key)}")
            
        if not isinstance(translations, dict):
            raise ValueError(f"Translations must be dict, got {type(translations)}")
            
        if Language.ENGLISH not in translations:
            translations[Language.ENGLISH] = key
            
        self._translations[key] = translations
        
    def get(self, key: str) -> str:
        """Get translation for the current language"""
        if not isinstance(key, str):
            return str(key)
            
        if key not in self._translations:
            return key
            
        translations = self._translations[key]
        if self._current_language not in translations:
            return translations.get(self._default_language, key)
            
        return translations[self._current_language]

    def add_range(self, key: str, ranges: Dict[Language, Dict[str, str]]) -> None:
        """Add a range entry with validation"""
        if not isinstance(key, str):
            raise ValueError(f"Range key must be string, got {type(key)}")
            
        if not isinstance(ranges, dict):
            raise ValueError(f"Ranges must be dict, got {type(ranges)}")
            
        if Language.ENGLISH not in ranges:
            ranges[Language.ENGLISH] = {'description': key}
            
        self._ranges[key] = ranges

    def get_range(self, range_key: str) -> str:
        """Get range description for current language with validation"""
        if not isinstance(range_key, str):
            return ""
            
        if range_key not in self._ranges:
            return ""
            
        ranges = self._ranges[range_key]
        current_range = ranges.get(self._current_language, ranges.get(self._default_language, {}))
        return current_range.get('description', "")
        
    def bulk_add_translations(self, translations_data: Dict[str, Dict[Language, str]]) -> None:
        """Add multiple translations at once"""
        if not isinstance(translations_data, dict):
            raise ValueError(f"Translations data must be dict, got {type(translations_data)}")
            
        for key, translations in translations_data.items():
            if key != 'ranges':  # Skip ranges key
                self.add_translation(key, translations)
            
    def bulk_add_ranges(self, ranges_data: Dict[str, Dict[Language, Dict[str, str]]]) -> None:
        """Add multiple ranges at once"""
        if not isinstance(ranges_data, dict):
            raise ValueError(f"Ranges data must be dict, got {type(ranges_data)}")
            
        for key, ranges in ranges_data.items():
            self.add_range(key, ranges)
            
    def initialize_debug(self, debug_level: int) -> None:
        """Initialize debug logging after plugin is started"""
        # Check translations for all languages
        for lang in Language:
            missing_translations = []
            for key, translations in self._translations.items():
                if lang not in translations:
                    missing_translations.append(key)
                    
            if missing_translations:
                log_debug(f"Missing {lang.name} translations for keys: {', '.join(missing_translations)}", 
                         DEBUG_BASIC, debug_level)
                    
        # Log translation coverage
        self._check_translation_coverage(debug_level)
        
    def _check_translation_coverage(self, debug_level: int) -> None:
        """Check and log translation coverage for current language"""
        missing_count = 0
        total_keys = len(self._translations)
        missing_keys = []
        
        for key, translations in self._translations.items():
            if self._current_language not in translations:
                missing_count += 1
                missing_keys.append(key)
        
        if missing_count > 0:
            coverage_pct = ((total_keys - missing_count)/total_keys) * 100
            log_debug(f"Translation coverage for {self._current_language.name}: "
                     f"{total_keys - missing_count}/{total_keys} ({coverage_pct:.1f}%)", 
                     DEBUG_BASIC, debug_level)
            log_debug(f"Missing translations for: {', '.join(missing_keys)}", 
                     DEBUG_BASIC, debug_level)
            
class BasePlugin:
    def __init__(self):
        self.debug_level = DEBUG_NONE
        self.active_connection = None
        self.name = None
        self.host = None
        self.port = None
        self.devices_parameters_list = []
        self.units = {}
        self.available_writes = {}
        self.dev_lists = {}
        self.translation_manager = TranslationManager()
        
        for command in SOCKET_COMMANDS.keys():
            self.dev_lists[command] = {}

        log_debug("Plugin initialized", DEBUG_BASIC, self.debug_level)

    def prepare_devices_list(self):
        log_debug("Preparing devices list", DEBUG_BASIC, self.debug_level)
        self.available_writes = {
            -1: Field(),
            1: Field(translate('Temp +-'), [a for a in range(-50, 51, 5)]),
            3: Field(translate('Heating mode'), [0, 1, 2, 3, 4]),
            4: Field(translate('Hot water mode'), [0, 1, 2, 3, 4]),
            105: Field(translate('DHW temp target'), [a for a in range(300, 651, 5)]),
            108: Field(translate('Cooling'), [0, 1])
        }
        
        # Define selector options as separate lists
        heating_mode_options = [
            'Automatic',
            '2nd heat source',
            'Party',
            'Holidays',
            'Off'
        ]

        self.devices_parameters_list = [
            # Heat supply/flow temperature sensor
            ['READ_CALCUL', 10, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('Heat supply temp')],

            # Return temperature sensor from heating system
            ['READ_CALCUL', 11, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('Heat return temp')],

            # Calculated target return temperature
            ['READ_CALCUL', 12, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('Return temp target')],

            # Outside ambient temperature sensor
            ['READ_CALCUL', 15, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('Outside temp')],

            # Average outside temperature over time
            ['READ_CALCUL', 16, (to_float, 10),
            dict(TypeName='Temperature', Used=0), translate('Outside temp avg')],

            # Domestic hot water current temperature
            ['READ_CALCUL', 17, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('DHW temp')],

            # Domestic hot water target temperature setting
            ['READ_PARAMS', 105, (to_float, 10),
            dict(Type=242, Subtype=1, Used=0), translate('DHW temp target'), (level_with_divider, 1/10)],

            # Source inlet temperature (from ground/well)
            ['READ_CALCUL', 19, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('WP source in temp')],

            # Source outlet temperature (to ground/well)
            ['READ_CALCUL', 20, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('WP source out temp')],

            # Mixing circuit 1 current temperature
            ['READ_CALCUL', 21, (to_float, 10),
            dict(TypeName='Temperature', Used=0), translate('MC1 temp')],

            # Mixing circuit 1 target temperature
            ['READ_CALCUL', 22, (to_float, 10),
            dict(TypeName='Temperature', Used=0), translate('MC1 temp target')],
            
            # Mixing circuit 2 current temperature
            ['READ_CALCUL', 24, (to_float, 10),
            dict(TypeName='Temperature', Used=0), translate('MC2 temp')],

            # Mixing circuit 2 target temperature
            ['READ_CALCUL', 25, (to_float, 10),
            dict(TypeName='Temperature', Used=0), translate('MC2 temp target')],

            # Heating operation mode selector switch
            ['READ_PARAMS', 3, (selector_switch_level_mapping, self.available_writes[3].get_val()),
            dict(TypeName='Selector Switch', Image=15, Used=1,
                Options={'LevelActions': '|' * len(heating_mode_options),
                        'LevelNames': translate_selector_options(heating_mode_options),
                        'LevelOffHidden': 'false',
                        'SelectorStyle': '1'}),
            translate('Heating mode'), (available_writes_level_with_divider, [10, 3])],

            # Hot water operation mode selector switch
            ['READ_PARAMS', 4, (selector_switch_level_mapping, self.available_writes[4].get_val()),
            dict(TypeName='Selector Switch', Image=15, Used=1,
                Options={'LevelActions': '|' * len(heating_mode_options),
                        'LevelNames': translate_selector_options(heating_mode_options),
                        'LevelOffHidden': 'false',
                        'SelectorStyle': '1'}),
            translate('Hot water mode'), (available_writes_level_with_divider, [10, 4])],

            # Cooling mode enable/disable switch
            ['READ_PARAMS', 108, [to_number],
            dict(TypeName='Switch', Image=16, Used=0), translate('Cooling'), [command_to_number]],

            ['READ_PARAMS', 1, (to_float, 10),
                dict(Type=242, Subtype=1, Used=1, 
                     Options={
                        "ValueStep": "0.5",   # Step increment of 0.5°C
                        "ValueMin": "-5",     # Minimum value of -5°C
                        "ValueMax": "5",      # Maximum value of 5°C
                        "ValueUnit": "°C"     # Unit to display
                    }
                ),
                translate('Temp +-'), (level_with_divider, 1/10)],

            # Current operating mode status text
            ['READ_CALCUL', 80, (to_text_state, [268, 0.1]),
            dict(TypeName='Text', Used=1), translate('Working mode')],

            # System flow rate measurement
            ['READ_CALCUL', 173, (to_float, 1),
            dict(TypeName='Custom', Used=1, Options={'Custom': '1;l/h'}), translate('Flow')],

            # Compressor frequency/speed
            ['READ_CALCUL', 231, (to_float, 1),
            dict(TypeName='Custom', Used=1, Options={'Custom': '1;Hz'}), translate('Compressor freq')],

            # Room temperature sensor reading
            ['READ_CALCUL', 227, (to_float, 10),
            dict(TypeName='Temperature', Used=0), translate('Room temp')],

            # Room temperature setpoint
            ['READ_CALCUL', 228, (to_float, 10),
            dict(TypeName='Temperature', Used=0), translate('Room temp target')],
            
            # Total electrical power consumption
            ['READ_CALCUL', 268, (to_instant_power, [268]),
            dict(TypeName='kWh', Used=1, Options={'EnergyMeterMode': '1'}),
            translate('Power total')],

            # Heating mode electrical power consumption
            ['READ_CALCUL', 268, (to_instant_power_split, [80, [0]]),
            dict(TypeName='kWh', Used=1, Options={'EnergyMeterMode': '1'}),
            translate('Power heating')],

            # Hot water mode electrical power consumption
            ['READ_CALCUL', 268, (to_instant_power_split, [80, [1]]),
            dict(TypeName='kWh', Used=1, Options={'EnergyMeterMode': '1'}),
            translate('Power DHW')],

            # Total heat output power
            ['READ_CALCUL', 257, (to_instant_power, [257]),
            dict(TypeName='kWh', Switchtype=4, Image=15, Used=1, Options={'EnergyMeterMode': '1'}),
            translate('Heat out total')],

            # Heating mode heat output power
            ['READ_CALCUL', 257, (to_instant_power_split, [80, [0]]),
            dict(TypeName='kWh', Switchtype=4, Image=15, Used=1, Options={'EnergyMeterMode': '1'}),
            translate('Heat out heating')],

            # Hot water mode heat output power
            ['READ_CALCUL', 257, (to_instant_power_split, [80, [1]]),
            dict(TypeName='kWh', Switchtype=4, Image=15, Used=1, Options={'EnergyMeterMode': '1'}),
            translate('Heat out DHW')],

            # Overall system COP (Coefficient of Performance)
            ['READ_CALCUL', 257, (to_cop_calculator, [257, 268]),
            dict(TypeName='Custom', Used=1, Options={'Custom': '1;COP'}),
            translate('COP total')],
            
            # Heating circulation pump speed percentage
            ['READ_CALCUL', 241, (to_float, 1),
            dict(TypeName='Percentage', Used=1), translate('Heating pump speed')],

            # Brine/well circulation pump speed percentage
            ['READ_CALCUL', 183, (to_float, 1),
            dict(TypeName='Percentage', Used=1), translate('Brine pump speed')],
            
            # Hot gas temperature monitoring
            ['READ_CALCUL', 14, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('Hot gas temp')],

            # Compressor suction temperature
            ['READ_CALCUL', 176, (to_float, 10),
            dict(TypeName='Temperature', Used=1), translate('Suction temp')],

            # Superheat monitoring
            ['READ_CALCUL', 178, (to_float, 10),
            dict(TypeName='Custom', Used=1, Options={'Custom': '1;K'}), translate('Superheat')],

            # High pressure monitoring
            ['READ_CALCUL', 180, (to_float, 100),
            dict(TypeName='Custom', Used=1, Options={'Custom': '1;bar'}), translate('High pressure')],

            # Low pressure monitoring
            ['READ_CALCUL', 181, (to_float, 100),
            dict(TypeName='Custom', Used=1, Options={'Custom': '1;bar'}), translate('Low pressure')],
            
            # Brine temperature difference (Source in - Source out)
            ['READ_CALCUL', [19, 20], (calculate_temp_diff, 10),
            dict(TypeName='Custom', Used=1, Options={'Custom': '1;K'}), translate('Brine temp diff')],
            
            # Heating temperature difference (Supply - Return)
            ['READ_CALCUL', [10, 11], (calculate_temp_diff, 10),
            dict(TypeName='Custom', Used=1, Options={'Custom': '1;K'}), translate('Heating temp diff')],         
        ]
        
        class Unit:
            def __init__(self, domoticz_id, message, address, read_conversion, dev_params, name, write_conversion=None):
                self.id = domoticz_id
                self.message = message
                self.address = address
                self.data_conversion_callback, *self._read_args = read_conversion

                self.dev_params = dev_params
                self.name = name
                if write_conversion is not None:
                    self.write_conversion_callback, *self._write_args = write_conversion
                else:
                    self.write_conversion_callback = write_conversion

            def update_domoticz_dev(self, data_list):
                update_device(Unit=self.id, **self.data_conversion_callback(data_list, self.address, *self._read_args))

            def prepare_data_to_send(self, **kwargs):
                return ('WRIT_PARAMS', self.address,
                        self.write_conversion_callback(*self._write_args, **kwargs))

        for dev_idx in range(len(self.devices_parameters_list)):
            tmp_unit = Unit(dev_idx + 1, *self.devices_parameters_list[dev_idx])
            tmp_unit.dev_params.update(dict(Name=tmp_unit.name, Unit=tmp_unit.id))

            self.units[tmp_unit.name] = tmp_unit
            self.dev_lists[tmp_unit.message][tmp_unit.id] = tmp_unit
            if tmp_unit.write_conversion_callback is not None:
                self.dev_lists['WRIT_PARAMS'][tmp_unit.id] = tmp_unit
                
    def _get_device_description(self, device_name: str) -> str:
        """Get range description for a device if available"""
        try:
            # Look up the range key for this device
            range_key = DEVICE_RANGE_MAPPINGS.get(device_name)
            if range_key:
                return self.translation_manager.get_range(range_key)
        except Exception as e:
            log_debug(f"Error getting description for {device_name}: {str(e)}", DEBUG_DEVICE, self.debug_level)
        return None    

    def create_devices(self):
        """Create or update devices with proper description handling and debug logging"""
        log_debug("Starting device creation process", DEBUG_BASIC, self.debug_level)
        
        # Prepare the device list
        log_debug("Preparing device list", DEBUG_DEVICE, self.debug_level)
        self.prepare_devices_list()
        
        # Log total number of devices to process
        total_devices = len(self.units)
        log_debug(f"Processing {total_devices} devices", DEBUG_DEVICE, self.debug_level)
        
        devices_created = 0
        devices_updated = 0
        
        for unit in self.units.values():
            try:
                # Get description if available for this device
                description = self._get_device_description(unit.name)
                if description:
                    unit.dev_params['Description'] = description
                
                if unit.id not in Devices:
                    # Log device creation with parameters if debug is enabled
                    if self.debug_level & DEBUG_DEVICE:
                        param_info = {k: v for k, v in unit.dev_params.items() 
                                    if k in ['TypeName', 'Options', 'Switchtype', 'Image']}
                        log_debug(f"Creating device {unit.id} ({unit.name}) with parameters: {param_info}", DEBUG_DEVICE, self.debug_level)
                    Domoticz.Device(**unit.dev_params).Create()
                    devices_created += 1
                else:
                    # Updating existing device
                    update_params = unit.dev_params.copy()
                    update_params.pop('Used', None)  # Don't change Used flag which can be set by user
                    if self.debug_level & DEBUG_DEVICE:
                        log_debug(f"Updating device {unit.id} ({unit.name})", DEBUG_DEVICE, self.debug_level)
                    update_device(**update_params)
                    devices_updated += 1
                    
            except Exception as e:
                error_msg = f"Error processing device {unit.name} (ID: {unit.id}): {str(e)}"
                log_debug(error_msg, DEBUG_DEVICE, self.debug_level)
                Domoticz.Error(error_msg)
        
        # Log summary of device creation/update process
        log_debug(f"Device creation complete - Created: {devices_created}, Updated: {devices_updated}, Total: {total_devices}", DEBUG_BASIC, self.debug_level)

    def initialize_connection(self):
        """Initialize socket connection with  logging"""
        try:
            self.active_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.active_connection.settimeout(5)
            self.active_connection.connect((self.host, int(self.port)))
            
            if self.debug_level == DEBUG_ALL:
                log_debug(f"Connected to {self.host}:{self.port} (Local: {self.active_connection.getsockname()})", 
                        DEBUG_CONN, self.debug_level)
            return True
        except Exception as e:
            error_msg = f"Connection failed to {self.host}:{self.port}: {str(e)}"
            log_debug(error_msg, DEBUG_CONN, self.debug_level)
            Domoticz.Error(error_msg)
            
            if hasattr(self, 'active_connection') and self.active_connection:
                self.active_connection.close()
                self.active_connection = None
            return False

    def send_message(self, command, address, value):
        """Send message to heat pump with logging"""
        try:
            if self.debug_level == DEBUG_ALL:
                log_debug(f"Sending {list(SOCKET_COMMANDS.keys())[list(SOCKET_COMMANDS.values()).index(command)]} command", 
                        DEBUG_PROTO, self.debug_level)
            
            # Send command and address
            self.active_connection.send(struct.pack('!i', command))
            self.active_connection.send(struct.pack('!i', address))

            # Handle write parameters
            if command == SOCKET_COMMANDS['WRIT_PARAMS']:
                self.active_connection.send(struct.pack('!i', value))

            # Verify command echo
            received_command = struct.unpack('!i', self.active_connection.recv(4))[0]
            if received_command != command:
                raise Exception(f"Command verification failed: sent {command}, received {received_command}")

            # Process response based on command type
            length = stat = 0
            data_list = []

            if command == SOCKET_COMMANDS['READ_PARAMS']:
                length = struct.unpack('!i', self.active_connection.recv(4))[0]
            elif command == SOCKET_COMMANDS['READ_CALCUL']:
                stat = struct.unpack('!i', self.active_connection.recv(4))[0]
                length = struct.unpack('!i', self.active_connection.recv(4))[0]

            # Read data if expected
            if length > 0:
                data_list = [struct.unpack('!i', self.active_connection.recv(4))[0] for _ in range(length)]

            return command, stat, length, data_list

        except Exception as e:
            error_msg = f"Message send failed: {str(e)}"
            log_debug(error_msg, DEBUG_PROTO, self.debug_level)
            Domoticz.Error(error_msg)
            return None

    def process_socket_message(self, command='READ_PARAMS', address=0, value=0):
        """Process socket messages with logging"""
        try:
            # Validate command and parameters
            if command not in SOCKET_COMMANDS:
                raise ValueError(f"Invalid command: {command}")

            if command == 'WRIT_PARAMS':
                if value not in self.available_writes[address].get_val():
                    raise ValueError(f"Invalid value for {self.available_writes[address].get_name()}: {value}")
            else:
                address = value = 0

            # Attempt communication with retries
            for attempt in range(2):
                try:
                    if self.initialize_connection():
                        result = self.send_message(SOCKET_COMMANDS[command], address, value)
                        if result:
                            if self.debug_level == DEBUG_ALL:
                                log_debug(f"{command}: Received {result[2]} values", DEBUG_PROTO, self.debug_level)
                            return result
                except socket.error as e:
                    if attempt == 0:  # Only log first attempt failure
                        log_debug(f"Socket error (retrying): {str(e)}", DEBUG_CONN, self.debug_level)
                finally:
                    if self.active_connection:
                        self.active_connection.close()
                        self.active_connection = None

            raise Exception(f"Failed after 2 attempts")

        except Exception as e:
            error_msg = f"Socket message processing failed: {str(e)}"
            log_debug(error_msg, DEBUG_PROTO, self.debug_level)
            Domoticz.Error(error_msg)
            return command, 0, 0, []

    def update(self, message):
        """Update devices for a specific message type with accurate update counting"""
        log_debug(f"Starting update for message type: {message}", DEBUG_BASIC, self.debug_level)
        
        try:
            # Process socket message
            log_debug(f"Processing socket message for {message}", DEBUG_PROTO, self.debug_level)
            command, stat, data_length, data_list = self.process_socket_message(message)
            
            if data_length > 0:
                log_debug(f"Received {data_length} values to process", DEBUG_DATA, self.debug_level)
                updates_count = 0
                
                # Update each device
                for device in self.dev_lists[message].values():
                    try:
                        # Create a copy of the device's current values
                        old_nValue = Devices[device.id].nValue
                        old_sValue = Devices[device.id].sValue
                        
                        # Update the device
                        device.update_domoticz_dev(data_list)
                        
                        # Check if values actually changed
                        if (Devices[device.id].nValue != old_nValue or 
                            Devices[device.id].sValue != old_sValue):
                            updates_count += 1
                            
                    except Exception as e:
                        error_msg = f"Error updating device {device.name}: {str(e)}"
                        log_debug(error_msg, DEBUG_DEVICE, self.debug_level)
                        Domoticz.Error(error_msg)
                        
                log_debug(f"{message}: Actually updated {updates_count} devices", DEBUG_DEVICE, self.debug_level)
                
            else:
                log_debug(f"No data received for message type: {message}", DEBUG_DATA, self.debug_level)
                    
        except Exception as e:
            error_msg = f"Error in update method: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, self.debug_level)
            Domoticz.Error(error_msg)

    def update_all(self):
        """Update all devices with accurate update counting"""
        if self.debug_level == DEBUG_ALL:
            log_debug("Heartbeat update started", DEBUG_BASIC, self.debug_level)
        
        try:
            for command_type in ['READ_CALCUL', 'READ_PARAMS']:
                result = self.process_socket_message(command_type)
                if result and result[2] > 0:  # If we got data
                    updates_count = 0
                    for device in self.dev_lists[command_type].values():
                        try:
                            # Store current values
                            old_nValue = Devices[device.id].nValue
                            old_sValue = Devices[device.id].sValue
                            
                            # Update device
                            if self._update_device(device, result[3]):
                                # Check if values actually changed
                                if (Devices[device.id].nValue != old_nValue or 
                                    Devices[device.id].sValue != old_sValue):
                                    updates_count += 1
                                    
                        except Exception as e:
                            log_debug(f"Failed to update {device.name}: {str(e)}", 
                                    DEBUG_DEVICE, self.debug_level)
                    
                    if self.debug_level == DEBUG_ALL:
                        log_debug(f"{command_type}: Actually updated {updates_count} devices", 
                                DEBUG_BASIC, self.debug_level)
                                
        except Exception as e:
            error_msg = f"Update failed: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, self.debug_level)
            Domoticz.Error(error_msg)

    def _update_device(self, device, data_list):
        """Helper method to update a single device"""
        try:
            device.update_domoticz_dev(data_list)
            return True
        except Exception as e:
            log_debug(f"Failed to update {device.name}: {str(e)}", DEBUG_DEVICE, self.debug_level)
            return False

    def onStart(self):
        """Initialize plugin with debug handling"""
        try:
            # Set debug level first
            self.debug_level = int(Parameters["Mode6"])
            
            if self.debug_level != DEBUG_NONE:
                Domoticz.Debugging(1)  # This is still needed for Debug() messages to show
            
            if self.debug_level != DEBUG_NONE:
                debug_categories = []
                if self.debug_level & DEBUG_BASIC:
                    debug_categories.append("Basic")
                if self.debug_level & DEBUG_DEVICE:
                    debug_categories.append("Device")
                if self.debug_level & DEBUG_CONN:
                    debug_categories.append("Connection")
                if self.debug_level & DEBUG_PROTO:
                    debug_categories.append("Protocol")
                if self.debug_level & DEBUG_DATA:
                    debug_categories.append("Data Processing")
                if self.debug_level == DEBUG_ALL:
                    debug_categories = ["All"]
                    
                log_debug("Debug logging enabled with level: " + str(self.debug_level), DEBUG_BASIC, self.debug_level)
                log_debug("Enabled debug categories: " + ", ".join(debug_categories), DEBUG_BASIC, self.debug_level)
                dump_config_to_log()
                
            # Initialize basic parameters first
            log_debug("Initializing plugin parameters", DEBUG_BASIC, self.debug_level)
            self.name = Parameters['Name']
            self.host = Parameters['Address']
            self.port = Parameters['Port']
            
            # Initialize translations and ranges
            log_debug("Initializing translation system", DEBUG_BASIC, self.debug_level)
            translations_data = {k: v for k, v in TRANSLATIONS.items() if k != 'ranges'}
            self.translation_manager.bulk_add_translations(translations_data)
            if 'ranges' in TRANSLATIONS:
                self.translation_manager.bulk_add_ranges(TRANSLATIONS['ranges'])
            set_language(Parameters["Mode3"])
            self.translation_manager.initialize_debug(self.debug_level)
            
            # Set heartbeat interval
            heartbeat_interval = int(Parameters['Mode2'])
            log_debug(f"Setting heartbeat interval to {heartbeat_interval}s", DEBUG_BASIC, self.debug_level)
            Domoticz.Heartbeat(heartbeat_interval)

            # Create devices
            log_debug("Creating devices", DEBUG_DEVICE, self.debug_level)
            self.create_devices()

            # Initialize connection only after host/port are set
            log_debug("Initializing connection", DEBUG_BASIC, self.debug_level)
            if not self.initialize_connection():
                log_debug("Failed to initialize connection - stopping initialization", DEBUG_BASIC, self.debug_level)
                return

            # Perform initial update
            log_debug("Performing initial device update", DEBUG_BASIC, self.debug_level)
            self.update_all()
            
            log_debug("Plugin initialization completed successfully", DEBUG_BASIC, self.debug_level)
            
        except Exception as e:
            error_msg = f"Error during plugin initialization: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, self.debug_level)
            Domoticz.Error(error_msg)

    def onStop(self):
        """Clean up plugin resources"""
        log_debug("Stopping plugin", DEBUG_BASIC, self.debug_level)
        
        try:
            if hasattr(self, 'active_connection') and self.active_connection:
                log_debug("Closing active connection", DEBUG_CONN, self.debug_level)
                self.active_connection.close()
                self.active_connection = None
                
            log_debug("Plugin stopped successfully", DEBUG_BASIC, self.debug_level)
        except Exception as e:
            error_msg = f"Error during plugin shutdown: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, self.debug_level)
            Domoticz.Error(error_msg)

    def onConnect(self, Connection, status, Description):
        """Handle connection events"""
        log_debug(f"Connection event:", DEBUG_CONN, self.debug_level)
        log_debug(f"  Address: {Connection.Address}:{Connection.Port}", DEBUG_CONN, self.debug_level)
        log_debug(f"  Status: {status}", DEBUG_CONN, self.debug_level)
        log_debug(f"  Description: {Description}", DEBUG_CONN, self.debug_level)

    def onDisconnect(self, Connection):
        """Handle disconnection events"""
        log_debug(f"Disconnect event:", DEBUG_CONN, self.debug_level)
        log_debug(f"  Address: {Connection.Address}:{Connection.Port}", DEBUG_CONN, self.debug_level)

    def onMessage(self, Connection, Data):
        """Handle incoming messages"""
        log_debug(f"Message received:", DEBUG_PROTO, self.debug_level)
        log_debug(f"  From: {Connection.Address}:{Connection.Port}", DEBUG_PROTO, self.debug_level)
        log_debug(f"  Data length: {len(Data) if Data else 0}", DEBUG_PROTO, self.debug_level)

    def onCommand(self, Unit, Command, Level, Hue):
        """Handle command events"""
        try:
            log_debug(f"Processing command:", DEBUG_PROTO, self.debug_level)
            log_debug(f"  Unit: {Unit}", DEBUG_PROTO, self.debug_level)
            log_debug(f"  Command: {Command}", DEBUG_PROTO, self.debug_level)
            log_debug(f"  Level: {Level}", DEBUG_PROTO, self.debug_level)
            
            # Prepare arguments
            argument_list = locals()
            argument_list.pop('self', None)
            
            # Process command
            log_debug("Preparing data to send", DEBUG_PROTO, self.debug_level)
            command_data = self.dev_lists['WRIT_PARAMS'][Unit].prepare_data_to_send(
                available_writes=self.available_writes,
                **argument_list)
                
            log_debug("Processing socket message", DEBUG_PROTO, self.debug_level)
            self.process_socket_message(*command_data)
            
            log_debug("Updating parameters after command", DEBUG_PROTO, self.debug_level)
            self.update('READ_PARAMS')
            
            log_debug("Command processing completed", DEBUG_PROTO, self.debug_level)
            
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, self.debug_level)
            Domoticz.Error(error_msg)

    def onHeartbeat(self):
        """Handle heartbeat events with consolidated logging"""
        if self.debug_level == DEBUG_ALL:
            log_debug("Heartbeat - Starting full device update", DEBUG_BASIC, self.debug_level)
        self.update_all()
        
    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        """
        Handle notifications received by Domoticz.

        This method logs all notification details and can trigger actions based on the notification's content.
        For example, if the Subject of the notification is 'Force Update', the plugin triggers a full device update.
        
        Parameters:
            Name (str): The name of the notification source.
            Subject (str): The subject of the notification.
            Text (str): The text/body of the notification.
            Status (str): The status associated with the notification.
            Priority (str): The priority level of the notification.
            Sound (str): Sound setting for the notification.
            ImageFile (str): The image file associated with the notification.
        """
        try:
            # Log the complete notification details for debugging
            log_debug(
                f"Notification received - Name: {Name}, Subject: {Subject}, Text: {Text}, "
                f"Status: {Status}, Priority: {Priority}, Sound: {Sound}, ImageFile: {ImageFile}",
                DEBUG_BASIC, self.debug_level)

            # Example: Trigger a full update if the subject is "Force Update"
            if Subject.lower() == "force update":
                log_debug("Force Update notification received; triggering full device update.", DEBUG_BASIC, self.debug_level)
                self.update_all()
            
        except Exception as e:
            error_msg = f"Error handling notification: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, self.debug_level)
            Domoticz.Error(error_msg)


def set_language(language_code: str) -> None:
    """Set the current language based on plugin parameter"""
    language_map = {
        '0': Language.ENGLISH,
        '1': Language.POLISH,
        '2': Language.DUTCH
    }
    language = language_map.get(language_code)
    if language is None:
        log_debug(f"Invalid language code: {language_code}, defaulting to English", DEBUG_BASIC, _plugin.debug_level)
        language = Language.ENGLISH
    else:
        log_debug(f"Setting language to: {language.name}", DEBUG_BASIC, _plugin.debug_level)
    _plugin.translation_manager.set_language(language)

def translate(key: str) -> str:
    """Get translation for a key"""
    return _plugin.translation_manager.get(key)


def translate_selector_options(options: list) -> str:
    """
    Translate a list of selector switch options and join them with pipes.

    For each option in the list, this function retrieves its translation using the
    plugin's translation manager. If the current language is not present in the
    translation dictionary for that option, it logs a message indicating that a
    translation is missing. Finally, it returns the translated options as a single
    string joined by the '|' character.

    Args:
        options (list): A list of option names (typically in English).

    Returns:
        str: A pipe-separated string of translated options.
    """
    translated_options = []
    for option in options:
        # Get translation or use original if not found.
        translated = translate(option)
        translated_options.append(translated)
        
        # Only log if the current language is not present in the translations for this option.
        translations = _plugin.translation_manager._translations.get(option, {})
        if _plugin.translation_manager._current_language not in translations:
            log_debug(f"Selector option missing translation: {option}", DEBUG_BASIC, _plugin.debug_level)
            
    return '|'.join(translated_options)


def is_translatable_key(text: str) -> bool:
    """
    Check if a text is a translatable key or translation value
    
    Args:
        text: Text to check
        
    Returns:
        bool: True if text is a translatable key or one of its translations
    """
    # Check if text is a direct key in translations
    if text in _plugin.translation_manager._translations:
        return True
        
    # Check if text is a translation value in any language
    for translations in _plugin.translation_manager._translations.values():
        for lang_value in translations.values():
            if isinstance(lang_value, str) and text == lang_value:
                return True
                
    return False

global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


def update_device(Unit: int = None, nValue: int = None, sValue: str = None, Image: int = None, 
                  SignalLevel: int = None, BatteryLevel: int = None, Options: dict = None, 
                  TimedOut: int = None, Name: str = None, TypeName: str = None, 
                  Type: int = None, Subtype: int = None, Switchtype: int = None,
                  Used: int = None, Description: str = None, Color: str = None):
    """
    Update a Domoticz device with update timing optimization.
    Delegates numeric (or text) change comparison to DeviceUpdateTracker and logs a combined update message.
    """
    
    # Ensure the device exists.
    if Unit not in Devices:
        log_debug(f"Device {Unit} not found - attempting to recreate devices", 
                  DEBUG_DEVICE, _plugin.debug_level)
        _plugin.create_devices()
        if Unit not in Devices:
            Domoticz.Error(f"Failed to create device {Unit}")
            return

    device = Devices[Unit]
    
    # Build update arguments from the current state.
    largs = {
        "nValue": device.nValue if device.nValue is not None else 0, 
        "sValue": str(device.sValue) if device.sValue is not None else ""
    }
    
    # Overwrite with new numeric values if provided.
    if nValue is not None:
        largs["nValue"] = nValue
    if sValue is not None:
        largs["sValue"] = str(sValue)
    
    # Process additional metadata parameters and track any differences.
    metadata_changes = []
    param_updates = {
        'Image': (Image, device.Image),
        'SignalLevel': (SignalLevel, device.SignalLevel),
        'BatteryLevel': (BatteryLevel, device.BatteryLevel),
        'Options': (Options, device.Options),
        'TimedOut': (TimedOut, device.TimedOut),
        'Type': (Type, device.Type),
        'Subtype': (Subtype, None),
        'Switchtype': (Switchtype, getattr(device, 'Switchtype', None)),
        'Description': (Description, device.Description),
        'Color': (Color, device.Color)
    }

    for param_name, (new_value, current_value) in param_updates.items():
        if new_value is not None and new_value != current_value:
            largs[param_name] = new_value
            metadata_changes.append(f"{param_name}: {current_value} -> {new_value}")

    # Handle name updates (with translation) if applicable.
    if Name is not None and Name != device.Name:
        current_name = (device.Name.replace(f"{Parameters['Name']} - ", "") 
                        if f"{Parameters['Name']} - " in device.Name 
                        else device.Name)
        if is_translatable_key(current_name):
            new_name = f"{Parameters['Name']} - {Name}"
            largs["Name"] = new_name
            metadata_changes.append(f"Name: {current_name} -> {Name}")

    # Use the DeviceUpdateTracker to decide whether the device values have changed.
    if not hasattr(_plugin, 'update_tracker'):
        _plugin.update_tracker = DeviceUpdateTracker()
        
    needs_update, update_reason, diff_message = _plugin.update_tracker.needs_update(
        device,
        {'nValue': largs['nValue'], 'sValue': largs['sValue']}
    )
    
    # Build and log a combined message that includes update decision, diff info, and metadata changes.
    if _plugin.debug_level & DEBUG_DEVICE:
        combined_message = f"Update decision for Device {Unit} ({device.Name}): {update_reason}"
        if diff_message:
            combined_message += f" -- {diff_message}"
        if metadata_changes:
            combined_message += f" | Metadata changes: {', '.join(metadata_changes)}"
        log_debug(combined_message, DEBUG_DEVICE, _plugin.debug_level)
    
    # Update the device only if needed.
    if needs_update or metadata_changes:
        try:
            Devices[Unit].Update(**largs)
        except Exception as e:
            Domoticz.Error(f"Error updating device {Unit} ({device.Name}): {str(e)}")
            

def dump_config_to_log():
    """Dump plugin configuration and device states to log with detailed formatting"""
    log_debug("=== Plugin Configuration ===", DEBUG_BASIC, _plugin.debug_level)
    
    # Log parameters
    log_debug("Parameters:", DEBUG_BASIC, _plugin.debug_level)
    for param_name, param_value in Parameters.items():
        if param_value:
            log_debug(f"  {param_name}: {param_value}", DEBUG_BASIC, _plugin.debug_level)

    # Log devices
    log_debug(f"\nRegistered Devices ({len(Devices)}):", DEBUG_BASIC, _plugin.debug_level)
    
    for device_unit, device in Devices.items():
        try:
            # Collect all device attributes
            device_info = {
                'Name': device.Name,
                'ID': device.ID,
                'Type': device.Type,
                'State': f"nValue={device.nValue}, sValue={device.sValue}"
            }
            
            # Add optional attributes if they exist and have values
            for attr in ['LastLevel', 'Image', 'SignalLevel', 'BatteryLevel', 'Used', 'Description']:
                if hasattr(device, attr):
                    value = getattr(device, attr)
                    if value is not None and (not isinstance(value, str) or value.strip()):
                        device_info[attr] = value
            
            # Add options if they exist and aren't empty
            if hasattr(device, 'Options') and device.Options:
                device_info['Options'] = device.Options
            
            # Format all info into a single line
            info_str = ', '.join(f"{k}: {v}" for k, v in device_info.items())
            log_debug(f"Device {device_unit}: {info_str}", DEBUG_BASIC, _plugin.debug_level)
                
        except Exception as e:
            log_debug(f"Error dumping config for device {device_unit}: {str(e)}", DEBUG_BASIC, _plugin.debug_level)
            
    log_debug("\n=== End Configuration Dump ===", DEBUG_BASIC, _plugin.debug_level)