# Luxtronik plugin based on sockets
# Author: ajarzyna, Rouzax, 2021
"""
<plugin key="luxtronik" name="Luxtronik Heat Pump Controller" author="Rouzax" version="1.0.0">
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
                <option label="Basic + Data Processing" value="17"/>  <!-- Basic + Data -->
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

# Debug level constants
DEBUG_NONE = 0                   # 0000 0000 - No debugging
DEBUG_BASIC = 1                  # 0000 0001 - Basic plugin operations (startup, device creation, etc.)
DEBUG_DEVICE = 2                 # 0000 0010 - Device updates and state changes
DEBUG_CONN = 4                   # 0000 0100 - Connection handling
DEBUG_PROTO = 8                  # 0000 1000 - Protocol/message details
DEBUG_DATA = 16                  # 0001 0000 - Data parsing and processing
DEBUG_ALL = -1                   # 1111 1111 - All debugging enabled

def log_debug(message, level, current_debug_level):
    """
    Log debug messages based on debug level.
    """
    if current_debug_level == DEBUG_NONE:
        return
        
    # If DEBUG_ALL is set, log everything
    if current_debug_level == DEBUG_ALL:
        Domoticz.Log(f"[ALL] {message}")
        return
        
    # Handle specific debug levels
    if level == DEBUG_BASIC and (current_debug_level & DEBUG_BASIC):
        Domoticz.Log(f"[BASIC]  {message}")
    elif level == DEBUG_DEVICE and (current_debug_level & DEBUG_DEVICE):
        Domoticz.Log(f"[DEVICE] {message}")
    elif level == DEBUG_CONN and (current_debug_level & DEBUG_CONN):
        Domoticz.Log(f"[CONN]   {message}")
    elif level == DEBUG_PROTO and (current_debug_level & DEBUG_PROTO):
        Domoticz.Log(f"[PROTO]  {message}")
    elif level == DEBUG_DATA and (current_debug_level & DEBUG_DATA):
        Domoticz.Log(f"[DATA]   {message}")

_IDS = {
    'Heat supply temp': [
        'Temp zasilania',
        'Aanvoertemp verw'
    ],
    'Heat return temp': [
        'Temp powrotu',
        'Retourtemp verw'
    ],
    'Return temp target': [
        'Temp powr cel',
        'Retourtemp doel'
    ],
    'Outside temp': [
        'Temp zewn',
        'Buitentemp'
    ],
    'Outside temp avg': [
        'Temp zewn śred',
        'Buitentemp gem'
    ],
    'DHW temp': [
        'Temp cwu',
        'Temp tapwater'
    ],
    'DHW temp target': [
        'Temp cwu cel',
        'Tapwater inst'
    ],
    'WP source in temp': [
        'Temp WP źródło wej',
        'WP bron in temp'
    ],
    'WP source out temp': [
        'Temp WP źródło wyj',
        'WP bron uit temp'
    ],
    'MC1 temp': [
        'Temp OM1',
        'Menggroep1 temp'
    ],
    'MC1 temp target': [
        'Temp OM1 cel',
        'Menggroep1 inst'
    ],
    'MC2 temp': [
        'Temp OM2',
        'Menggroep2 temp'
    ],
    'MC2 temp target': [
        'Temp OM2 cel',
        'Menggroep2 inst'
    ],
    'Heating mode': [
        'Obieg grzewczy',
        'Verwarmen'
    ],
    'Hot water mode': [
        'Woda użytkowa',
        'Warmwater'
    ],
    'Cooling': [
        'Chłodzenie',
        'Koeling'
    ],
    'Automat.|2nd h. source|Party|Holidays|Off': [
        'Automat.|II źr. ciepła|Party|Wakacje|Wył.',
        'Automatisch|2e warm.opwek|Party|Vakantie|Uit',
    ],
    'No requirement': [
        'Brak zapotrzebowania',
        'Geen warmtevraag',
    ],
    'Swimming pool mode / Photovaltaik': [
        'Tryb basen / Fotowoltaika',
        'Zwembad / Fotovoltaïek'
    ],
    'EVUM': [
        'EVU',
        'EVU'
    ],
    'Defrost': [
        'Rozmrażanie',
        'Ontdooien'
    ],
    'Heating external source mode': [
        'Ogrzewanie z zewnętrznego źródła',
        'Verwarmen 2e warm.opwek'
    ],
    'Temp +-': [
        'Temp +-',
        'Temp +-'
    ],
    'Working mode': [
        'Stan pracy',
        'Bedrijfsmode'
    ],
    'Flow': [
        'Przepływ',
        'Debiet'
    ],
    'Compressor freq': [
        'Częst sprężarki',
        'Compr freq'
    ],
    'Room temp': [
        'Temp pokojowa',
        'Ruimtetemp act'
    ],
    'Room temp target': [
        'Temp pokoj cel',
        'Ruimtetemp gew'
    ],
    'Power total': [
        'Pobór mocy',
        'Energie totaal'
    ],
    'Power heating': [
        'Pobór grz',
        'Energie verw'
    ],
    'Power DHW': [
        'Pobór cwu',
        'Energie warmw'
    ],
    'Heat out total': [
        'Moc grz razem',
        'Verwarm totaal'
    ],
    'Heat out heating': [
        'Moc grz ogrz',
        'Verwarm verw'
    ],
    'Heat out DHW': [
        'Moc grz cwu',
        'Verwarm warmw'
    ],
    'COP total': [
        'COP razem',
        'COP totaal'
    ]
}

_IDS_STR = str(_IDS)

SOCKET_COMMANDS = {
    'WRIT_PARAMS': 3002,
    'READ_PARAMS': 3003,
    'READ_CALCUL': 3004,
    'READ_VISIBI': 3005
}

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
    
    
def to_instant_power(data_list: list, power_data_idx: int, *args) -> dict:
    """Converts instant power to string."""
    instant_power = float(data_list[power_data_idx])
    return {'sValue': f"{instant_power};0"}

def to_instant_power_split(data_list: list, power_data_idx: int, additional_data: list) -> dict:
    """Splits instant power into heating or hot water based on operating mode."""
    state_idx, valid_states = additional_data
    instant_power = float(data_list[power_data_idx])
    
    # Check operating mode
    current_state = int(data_list[state_idx])
    
    # If not in a valid state, return 0 power
    if current_state not in valid_states:
        return {'sValue': f"0;0"}
        
    return {'sValue': f"{instant_power};0"}


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
    """Converts heat pump state to text status"""
    # Operating modes based on ID_WEB_WP_BZ_akt values
    mode_names = {
        0: ids('Heating mode'),      # heating
        1: ids('Hot water mode'),    # hot water
        2: ids('Swimming pool mode / Photovaltaik'),
        3: ids('Cooling'),
        4: ids('No requirement')     # off/no requirement
    }
    
    power_idx, power_threshold = config
    
    # Get current power consumption
    current_power = float(data_list[power_idx])
    
    # Get current mode
    current_mode = data_list[data_idx]
  
    # If power consumption is below threshold, return "No requirement"
    if current_power <= power_threshold:
        return {'nValue': 0, 'sValue': ids('No requirement')}
    
    # Map mode to text
    state_text = mode_names.get(current_mode, ids('No requirement'))
    return {'nValue': 0, 'sValue': state_text}


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


def ids(text):
    """Returns translated text based on language."""	
    return _IDS[text][int(Parameters["Mode3"])-1] if int(Parameters["Mode3"]) else text


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

class BasePlugin:
    def __init__(self):
        # Initialize debug_level with a default value
        self.debug_level = DEBUG_NONE  # Set to 0 by default
        
        self.active_connection = None
        self.name = None
        self.host = None
        self.port = None

        self.devices_parameters_list = []

        self.units = {}
        self.available_writes = {}
        self.dev_lists = {}
        for command in SOCKET_COMMANDS.keys():
            self.dev_lists[command] = {}

        log_debug("Plugin initialized", DEBUG_BASIC, self.debug_level)

    def prepare_devices_list(self):
        log_debug("Preparing devices list", DEBUG_BASIC, self.debug_level)
        self.available_writes = {
            -1: Field(),
            1: Field(ids('Temp +-'), [a for a in range(-50, 51, 5)]),
            3: Field(ids('Heating mode'), [0, 1, 2, 3, 4]),
            4: Field(ids('Hot water mode'), [0, 1, 2, 3, 4]),
            105: Field(ids('DHW temp target'), [a for a in range(300, 651, 5)]),
            108: Field(ids('Cooling'), [0, 1])
        }

        work_modes_mapping = [(3, ids('Heating mode')),
                              (4, ids('Hot water mode')),
                              (2, ids('Swimming pool mode / Photovaltaik')),
                              (2, ids('EVUM')),
                              (1, ids('Defrost')),
                              (0, ids('No requirement')),
                              (4, ids('Heating external source mode')),
                              (1, ids('Cooling'))]

        hot_water_temps = '|'.join([str(a / 10) for a in self.available_writes[105].get_val()])
        heating_temps = '|'.join([str(a / 10) for a in self.available_writes[1].get_val()])

        self.devices_parameters_list = [
            # 0 Data group/socket command,
            # 1 idx in returned data,
            # 2 tuple(data modification callback, list of additional read data (conversion, indexes, relates)),
            # 3 Domoticz devices dictionary options,
            # 4 Name of the domoticz device,
            # 5 tuple(write callback, list of additional write needed data (conversion, indexes))
            ['READ_CALCUL', 10, (to_float, 10),
             dict(TypeName='Temperature', Used=1), ids('Heat supply temp')],

            ['READ_CALCUL', 11, (to_float, 10),
             dict(TypeName='Temperature', Used=1), ids('Heat return temp')],

            ['READ_CALCUL', 12, (to_float, 10),
             dict(TypeName='Temperature', Used=1), ids('Return temp target')],

            ['READ_CALCUL', 15, (to_float, 10),
             dict(TypeName='Temperature', Used=1), ids('Outside temp')],

            ['READ_CALCUL', 16, (to_float, 10),
             dict(TypeName='Temperature', Used=0), ids('Outside temp avg')],

            ['READ_CALCUL', 17, (to_float, 10),
             dict(TypeName='Temperature', Used=1), ids('DHW temp')],

            ['READ_PARAMS', 105, (to_float, 10),
            dict(Type=242, Subtype=1, Used=0), ids('DHW temp target'), (level_with_divider, 1/10)],

            ['READ_CALCUL', 19, (to_float, 10),
             dict(TypeName='Temperature', Used=1), ids('WP source in temp')],

            ['READ_CALCUL', 20, (to_float, 10),
             dict(TypeName='Temperature', Used=1), ids('WP source out temp')],

            ['READ_CALCUL', 21, (to_float, 10),
             dict(TypeName='Temperature', Used=0), ids('MC1 temp')],

            ['READ_CALCUL', 22, (to_float, 10),
             dict(TypeName='Temperature', Used=0), ids('MC1 temp target')],
            
            ['READ_CALCUL', 24, (to_float, 10),
             dict(TypeName='Temperature', Used=0), ids('MC2 temp')],

            ['READ_CALCUL', 25, (to_float, 10),
             dict(TypeName='Temperature', Used=0), ids('MC2 temp target')],

            ['READ_PARAMS', 3, (selector_switch_level_mapping, self.available_writes[3].get_val()),
             dict(TypeName='Selector Switch', Image=7, Used=1,
                  Options={'LevelActions': '|||||',
                           'LevelNames': ids('Automat.|2nd h. source|Party|Holidays|Off'),
                           'LevelOffHidden': 'false',
                           'SelectorStyle': '1'}),
             ids('Heating mode'), (available_writes_level_with_divider, [10, 3])],

            ['READ_PARAMS', 4, (selector_switch_level_mapping, self.available_writes[4].get_val()),
             dict(TypeName='Selector Switch', Image=7, Used=1,
                  Options={'LevelActions': '|||||',
                           'LevelNames': ids('Automat.|2nd h. source|Party|Holidays|Off'),
                           'LevelOffHidden': 'false',
                           'SelectorStyle': '1'}),
             ids('Hot water mode'), (available_writes_level_with_divider, [10, 4])],

            ['READ_PARAMS', 108, [to_number],
             dict(TypeName='Switch', Image=9, Used=0), ids('Cooling'), [command_to_number]],

            ['READ_PARAMS', 1, (to_float, 10),
             dict(Type=242, Subtype=1, Used=0), ids('Temp +-'), (level_with_divider, 1/10)],

            ['READ_CALCUL', 80, (to_text_state, [268, 0.1]),
             dict(TypeName='Text', Used=1), ids('Working mode')],

            ['READ_CALCUL', 173, (to_float, 1),
             dict(TypeName='Custom', Used=1, Options={'Custom': '1;l/h'}), ids('Flow')],

            ['READ_CALCUL', 231, (to_float, 1),
             dict(TypeName='Custom', Used=0, Options={'Custom': '1;Hz'}), ids('Compressor freq')],

            ['READ_CALCUL', 227, (to_float, 10),
             dict(TypeName='Temperature', Used=0), ids('Room temp')],

            ['READ_CALCUL', 228, (to_float, 10),
             dict(TypeName='Temperature', Used=0), ids('Room temp target')],
            
            # Power consumption
            ['READ_CALCUL', 268, (to_instant_power, [268]),
             dict(TypeName='kWh', Used=1,
                  Options={'EnergyMeterMode': '1'}),
             ids('Power total')],

            # Power consumption for heating mode
            ['READ_CALCUL', 268, (to_instant_power_split, [80, [0]]),
             dict(TypeName='kWh', Used=1,
                  Options={'EnergyMeterMode': '1'}),
             ids('Power heating')],

            # Power consumption for hot water mode
            ['READ_CALCUL', 268, (to_instant_power_split, [80, [1]]),
             dict(TypeName='kWh', Used=1,
                  Options={'EnergyMeterMode': '1'}),
             ids('Power DHW')],

            # Heat output total
            ['READ_CALCUL', 257, (to_instant_power, [257]),
             dict(TypeName='kWh', Switchtype=4, Image=15, Used=1,
                  Options={'EnergyMeterMode': '1'}),
             ids('Heat out total')],

            # Heat output heating mode
            ['READ_CALCUL', 257, (to_instant_power_split, [80, [0]]),
             dict(TypeName='kWh', Switchtype=4, Image=15, Used=1,
                  Options={'EnergyMeterMode': '1'}),
             ids('Heat out heating')],

            # Heat output hot water mode
            ['READ_CALCUL', 257, (to_instant_power_split, [80, [1]]),
             dict(TypeName='kWh', Switchtype=4, Image=15, Used=1,
                  Options={'EnergyMeterMode': '1'}),
             ids('Heat out DHW')],

            # COP calculated over total
            ['READ_CALCUL', 257, (to_cop_calculator, [257, 268]),
             dict(TypeName='Custom', Used=1,
                  Options={'Custom': '1;COP'}),
             ids('COP total')],
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

    def create_devices(self):
        self.prepare_devices_list()
        for unit in self.units.values():
            if unit.id not in Devices:
                Domoticz.Device(**unit.dev_params).Create()

            else:
                # Do not change "Used" option which can be set by user.
                update_params = unit.dev_params
                update_params.pop('Used', None)
                update_device(**update_params)

    def initialize_connection(self):
        """
        Initialize socket connection with comprehensive debug logging
        """
        # Log connection attempt start
        log_debug(f"Starting connection initialization to {self.host}:{self.port}", DEBUG_CONN, self.debug_level)

        # Log socket creation
        log_debug("Creating socket object", DEBUG_CONN, self.debug_level)
        self.active_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set socket options if needed
        try:
            # Set socket timeout to prevent hanging
            self.active_connection.settimeout(5)
            log_debug("Socket timeout set to 5 seconds", DEBUG_PROTO, self.debug_level)

            # Attempt connection
            log_debug(f"Attempting connection to {self.host}:{self.port}...", DEBUG_CONN, self.debug_level)
            start_time = time.time()
            self.active_connection.connect((self.host, int(self.port)))
            connect_time = time.time() - start_time

            # Log successful connection with timing
            log_debug(f"Connection established successfully in {connect_time:.2f}s", DEBUG_CONN, self.debug_level)
            log_debug(f"Socket details - Local: {self.active_connection.getsockname()}, Remote: {self.active_connection.getpeername()}", DEBUG_CONN, self.debug_level)

            return True

        except socket.timeout as timeout_err:
            error_msg = f"Connection timed out after 5s: {str(timeout_err)}"
            log_debug(error_msg, DEBUG_CONN, self.debug_level)
            Domoticz.Error(error_msg)

        except socket.gaierror as dns_err:
            error_msg = f"DNS resolution failed for {self.host}: {str(dns_err)}"
            log_debug(error_msg, DEBUG_CONN, self.debug_level)
            Domoticz.Error(error_msg)

        except OSError as os_err:
            error_msg = f"Connection failed to {self.host}:{self.port} - {str(os_err)}"
            log_debug(error_msg, DEBUG_CONN, self.debug_level)
            Domoticz.Error(error_msg)

            # Additional debug info for specific error codes
            if os_err.errno == errno.ECONNREFUSED:
                log_debug("Connection was actively refused by the host", DEBUG_CONN, self.debug_level)
            elif os_err.errno == errno.ENETUNREACH:
                log_debug("Network is unreachable", DEBUG_CONN, self.debug_level)

        except Exception as e:
            error_msg = f"Unexpected error during connection: {str(e)}"
            log_debug(error_msg, DEBUG_CONN, self.debug_level)
            Domoticz.Error(error_msg)

        # Only close connection on error
        if hasattr(self, 'active_connection') and self.active_connection and not self.active_connection._closed:
            log_debug("Cleaning up socket after failed connection", DEBUG_CONN, self.debug_level)
            self.active_connection.close()
            self.active_connection = None

        return False

    def send_message(self, command, address, value):
        """
        Send message to heat pump with comprehensive debug logging and error handling
        """
        # Log message details
        log_debug(f"Preparing to send message:", DEBUG_PROTO, self.debug_level)
        log_debug(f"  Command: {command} ({SOCKET_COMMANDS.get(command, 'Unknown')})", DEBUG_PROTO, self.debug_level)
        log_debug(f"  Address: {address}", DEBUG_PROTO, self.debug_level)
        log_debug(f"  Value: {value}", DEBUG_PROTO, self.debug_level)

        try:
            # Send command
            log_debug(f"Sending command packet: {command}", DEBUG_PROTO, self.debug_level)
            self.active_connection.send(struct.pack('!i', command))

            # Send address
            log_debug(f"Sending address packet: {address}", DEBUG_PROTO, self.debug_level)
            self.active_connection.send(struct.pack('!i', address))

            # Handle write parameters
            if command == SOCKET_COMMANDS['WRIT_PARAMS']:
                log_debug(f"Sending address packet: {address}", DEBUG_PROTO, self.debug_level)
                self.active_connection.send(struct.pack('!i', value))

            # Receive and verify command echo
            received_command = struct.unpack('!i', self.active_connection.recv(4))[0]
            if received_command != command:
                error_msg = f"Command verification failed. Sent: {command}, Received: {received_command}"
                log_debug(error_msg, DEBUG_PROTO, self.debug_level)
                Domoticz.Error(error_msg)
                return None

            length = 0
            stat = 0
            data_list = []

            # Handle different command types
            if command == SOCKET_COMMANDS['READ_PARAMS']:
                length = struct.unpack('!i', self.active_connection.recv(4))[0]
                log_debug(f"READ_PARAMS - Expecting {length} parameters", DEBUG_PROTO, self.debug_level)

            elif command == SOCKET_COMMANDS['READ_CALCUL']:
                stat = struct.unpack('!i', self.active_connection.recv(4))[0]
                length = struct.unpack('!i', self.active_connection.recv(4))[0]
                log_debug(f"READ_CALCUL - Status: {stat}, Expecting {length} values", DEBUG_PROTO, self.debug_level)

            elif command == SOCKET_COMMANDS['READ_VISIBI']:
                log_debug("READ_VISIBI command - No data expected", DEBUG_PROTO, self.debug_level)

            elif command == SOCKET_COMMANDS['WRIT_PARAMS']:
                log_debug("WRIT_PARAMS command completed", DEBUG_PROTO, self.debug_level)

            # Read data if length > 0
            if length > 0:
                log_debug(f"Reading {length} data values...", DEBUG_DATA, self.debug_level)
                for i in range(length):
                    value = struct.unpack('!i', self.active_connection.recv(4))[0]
                    data_list.append(value)
                    # log_debug(f"Read value {i+1}/{length}: {value}", DEBUG_DATA, self.debug_level)

            return command, stat, length, data_list

        except Exception as e:
            error_msg = f"Unexpected error in send_message: {str(e)}"
            log_debug(error_msg, DEBUG_PROTO, self.debug_level)
            Domoticz.Error(error_msg)
            return None

    def process_socket_message(self, command='READ_PARAMS', address=0, value=0):
        """
        Process and validate socket messages with comprehensive error handling and debugging
        """
        log_debug(f"Processing socket message:", DEBUG_PROTO, self.debug_level)
        log_debug(f"  Command: {command}", DEBUG_PROTO, self.debug_level)
        log_debug(f"  Address: {address}", DEBUG_PROTO, self.debug_level)
        log_debug(f"  Value: {value}", DEBUG_PROTO, self.debug_level)

        # Validate command
        if command not in SOCKET_COMMANDS:
            error_msg = f"Invalid command: {command}. Valid commands: {list(SOCKET_COMMANDS.keys())}"
            log_debug(error_msg, DEBUG_PROTO, self.debug_level)
            Domoticz.Error(error_msg)
            return command, 0, 0, []

        # Handle write parameters validation
        if command == 'WRIT_PARAMS':
            try:
                available_values = self.available_writes[address].get_val()
                param_name = self.available_writes[address].get_name()

                log_debug(f"Validating write parameter:", DEBUG_DATA, self.debug_level)
                log_debug(f"  Parameter: {param_name}", DEBUG_DATA, self.debug_level)
                log_debug(f"  Available values: {available_values}", DEBUG_DATA, self.debug_level)
                log_debug(f"  Requested value: {value}", DEBUG_DATA, self.debug_level)

                if value not in available_values:
                    error_msg = (f"Invalid value for parameter '{param_name}': {value}. "
                            f"Must be one of: {available_values}")
                    log_debug(error_msg, DEBUG_DATA, self.debug_level)
                    Domoticz.Error(error_msg)
                    return command, 0, 0, []

            except KeyError:
                error_msg = f"Invalid write parameter address: {address}"
                log_debug(error_msg, DEBUG_PROTO, self.debug_level)
                Domoticz.Error(error_msg)
                return command, 0, 0, []
        else:
            # Reset address and value for non-write commands
            log_debug("Non-write command, resetting address and value to 0", DEBUG_PROTO, self.debug_level)
            address = 0
            value = 0

        # Attempt to send message
        retry_count = 0
        max_retries = 2

        while retry_count < max_retries:
            try:
                log_debug(f"Sending message (attempt {retry_count + 1}/{max_retries})", DEBUG_PROTO, self.debug_level)

                # Initialize connection first
                if not self.initialize_connection():
                    log_debug("Failed to initialize connection", DEBUG_CONN, self.debug_level)
                    retry_count += 1
                    continue

                # Try to send message and get response
                result = self.send_message(SOCKET_COMMANDS[command], address, value)
                
                if result is not None:
                    log_debug("Message sent and received successfully", DEBUG_CONN, self.debug_level)
                    return result

                log_debug("Received None response from send_message", DEBUG_PROTO, self.debug_level)

            except socket.error as e:
                error_msg = f"Socket error (attempt {retry_count + 1}): {str(e)}"
                log_debug(error_msg, DEBUG_CONN, self.debug_level)

            except Exception as e:
                error_msg = f"Unexpected error processing message: {str(e)}"
                log_debug(error_msg, DEBUG_PROTO, self.debug_level)
                Domoticz.Error(error_msg)
                break

            finally:
                # Always clean up the connection after each attempt
                if hasattr(self, 'active_connection') and self.active_connection:
                    log_debug("Closing connection", DEBUG_CONN, self.debug_level)
                    self.active_connection.close()
                    self.active_connection = None

            retry_count += 1

        # If we get here, all attempts failed
        error_msg = f"Failed to process socket message after {max_retries} attempts"
        log_debug(error_msg, DEBUG_PROTO, self.debug_level)
        Domoticz.Error(error_msg)

        # Return empty result
        log_debug("Returning empty result", DEBUG_PROTO, self.debug_level)
        return command, 0, 0, []

    def update(self, message):
        """Update devices for a specific message type with debug logging"""
        log_debug(f"Starting update for message type: {message}", DEBUG_BASIC, self.debug_level)
        
        try:
            # Process socket message
            log_debug(f"Processing socket message for {message}", DEBUG_PROTO, self.debug_level)
            command, stat, data_length, data_list = self.process_socket_message(message)
            
            if data_length > 0:
                log_debug(f"Received {data_length} values to process", DEBUG_DATA, self.debug_level)
                devices_updated = 0
                
                # Update each device
                for device in self.dev_lists[message].values():
                    try:
                        log_debug(f"Updating device: {device.name}", DEBUG_DEVICE, self.debug_level)
                        device.update_domoticz_dev(data_list)
                        devices_updated += 1
                    except Exception as e:
                        error_msg = f"Error updating device {device.name}: {str(e)}"
                        log_debug(error_msg, DEBUG_DEVICE, self.debug_level)
                        Domoticz.Error(error_msg)
                        
                log_debug(f"Update complete - {devices_updated} devices updated", DEBUG_DEVICE, self.debug_level)
            else:
                log_debug(f"No data received for message type: {message}", DEBUG_DATA, self.debug_level)
                
        except Exception as e:
            error_msg = f"Error in update method: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, self.debug_level)
            Domoticz.Error(error_msg)

    def update_all(self):
        """Update all device types"""
        log_debug("Starting full update of all devices", DEBUG_BASIC, self.debug_level)
        
        try:
            log_debug("Updating calculated values", DEBUG_BASIC, self.debug_level)
            self.update('READ_CALCUL')
            
            log_debug("Updating parameters", DEBUG_BASIC, self.debug_level)
            self.update('READ_PARAMS')
            
            log_debug("Full update completed", DEBUG_BASIC, self.debug_level)
        except Exception as e:
            error_msg = f"Error in update_all method: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, self.debug_level)
            Domoticz.Error(error_msg)

    def onStart(self):
        """Initialize plugin with corrected debug handling"""
        try:
            # Set debug level
            self.debug_level = int(Parameters["Mode6"])
            
            # We no longer need to call Domoticz.Debugging()
            # Just start logging if debug is enabled
            if self.debug_level != DEBUG_NONE:
                # Log which debug categories are enabled
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

            # Initialize basic parameters
            log_debug("Initializing plugin parameters", DEBUG_BASIC, self.debug_level)
            self.name = Parameters['Name']
            self.host = Parameters['Address']
            self.port = Parameters['Port']
            
            # Set heartbeat interval
            heartbeat_interval = int(Parameters['Mode2'])
            log_debug(f"Setting heartbeat interval to {heartbeat_interval}s", DEBUG_BASIC, self.debug_level)
            Domoticz.Heartbeat(heartbeat_interval)

            # Create devices
            log_debug("Creating devices", DEBUG_DEVICE, self.debug_level)
            self.create_devices()

            # Initialize connection
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
        """Handle heartbeat events"""
        log_debug("Heartbeat received - updating all devices", DEBUG_BASIC, self.debug_level)
        self.update_all()


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


def update_device(Unit: int = None, nValue: int = None, sValue: str = None, Image: int = None, SignalLevel: int = None,
                  BatteryLevel: int = None, Options: dict = None, TimedOut: int = None, Name: str = None,
                  TypeName: str = None, Type: int = None, Subtype: int = None, Switchtype: int = None,
                  Used: int = None, Description: str = None, Color: str = None):
    """
    Update Domoticz device with comprehensive validation and debug logging
    """
    # Validate device exists
    if Unit not in Devices:
        log_debug(f"Device {Unit} not found - attempting to recreate devices", DEBUG_DEVICE, _plugin.debug_level)
        _plugin.create_devices()
        if Unit not in Devices:
            error_msg = f"Failed to create device {Unit}"
            log_debug(error_msg, DEBUG_DEVICE, _plugin.debug_level)
            Domoticz.Error(error_msg)
            return

    log_debug(f"Updating device {Unit} ({Devices[Unit].Name})", DEBUG_DEVICE, _plugin.debug_level)
    
    # Build update arguments
    largs = {}
    update_needed = False

    # Handle required parameters nValue and sValue
    largs["nValue"] = 0
    if nValue is not None:
        log_debug(f"  Setting nValue: {nValue}", DEBUG_DEVICE, _plugin.debug_level)
        largs["nValue"] = nValue
        update_needed = True
    elif Devices[Unit].nValue is not None:
        largs["nValue"] = Devices[Unit].nValue

    largs["sValue"] = ""
    if sValue is not None:
        log_debug(f"  Setting sValue: {sValue}", DEBUG_DEVICE, _plugin.debug_level)
        largs["sValue"] = str(sValue)
        update_needed = True
    elif Devices[Unit].sValue is not None:
        largs["sValue"] = str(Devices[Unit].sValue)

    # Process optional parameters
    try:
        device = Devices[Unit]
        
        # Check and log each parameter update
        param_updates = {
            'Image': (Image, device.Image),
            'SignalLevel': (SignalLevel, device.SignalLevel),
            'BatteryLevel': (BatteryLevel, device.BatteryLevel),
            'Options': (Options, device.Options),
            'TimedOut': (TimedOut, device.TimedOut),
            'Type': (Type, device.Type),
            'Subtype': (Subtype, None),  # Always update if provided
            'SwitchType': (Switchtype, getattr(device, 'SwitchType', None)),
            'Used': (Used, device.Used),
            'Description': (Description, device.Description),
            'Color': (Color, device.Color)
        }

        # Process name separately due to special formatting
        if Name is not None and Name != device.Name:
            if bool(re.search(device.Name.replace(
                f"{Parameters['Name']} - " if f"{Parameters['Name']} - " in device.Name else "", 
                ""), _IDS_STR)):
                new_name = f"{Parameters['Name']} - {Name}"
                log_debug(f"  Updating name to: {new_name}", DEBUG_DEVICE, _plugin.debug_level)
                largs["Name"] = new_name
                update_needed = True

        # Process other parameters
        for param_name, (new_value, current_value) in param_updates.items():
            if new_value is not None and new_value != current_value:
                log_debug(f"  Updating {param_name}: {new_value}", DEBUG_DEVICE, _plugin.debug_level)
                largs[param_name] = new_value
                update_needed = True

    except Exception as e:
        error_msg = f"Error preparing device update parameters: {str(e)}"
        log_debug(error_msg, DEBUG_DEVICE, _plugin.debug_level)
        Domoticz.Error(error_msg)
        return

    # Perform update if needed
    if update_needed:
        try:
            log_debug(f"Updating device {Unit} with parameters: {str(largs)}", DEBUG_DEVICE, _plugin.debug_level)
            Devices[Unit].Update(**largs)
            log_debug(f"Device {Unit} updated successfully", DEBUG_DEVICE, _plugin.debug_level)
        except Exception as e:
            error_msg = f"Error updating device {Unit}: {str(e)}"
            log_debug(error_msg, DEBUG_DEVICE, _plugin.debug_level)
            Domoticz.Error(error_msg)
    else:
        log_debug(f"No updates needed for device {Unit}", DEBUG_DEVICE, _plugin.debug_level)

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
            log_debug(f"\nDevice Unit {device_unit}:", DEBUG_BASIC, _plugin.debug_level)
            log_debug(f"  Name:        {device.Name}", DEBUG_BASIC, _plugin.debug_level)
            log_debug(f"  ID:          {device.ID}", DEBUG_BASIC, _plugin.debug_level)
            log_debug(f"  Type:        {device.Type}", DEBUG_BASIC, _plugin.debug_level)
            log_debug(f"  State:       nValue={device.nValue}, sValue={device.sValue}", DEBUG_BASIC, _plugin.debug_level)
            
            # Log additional device attributes if they exist
            for attr in ['LastLevel', 'Image', 'SignalLevel', 'BatteryLevel', 'Used', 'Description']:
                if hasattr(device, attr):
                    value = getattr(device, attr)
                    if value is not None:
                        log_debug(f"  {attr}:        {value}", DEBUG_BASIC, _plugin.debug_level)
            
            # Log options if they exist and are not empty
            if hasattr(device, 'Options') and device.Options:
                log_debug(f"  Options:     {device.Options}", DEBUG_BASIC, _plugin.debug_level)
                
        except Exception as e:
            error_msg = f"Error dumping config for device {device_unit}: {str(e)}"
            log_debug(error_msg, DEBUG_BASIC, _plugin.debug_level)
            Domoticz.Error(error_msg)
            
    log_debug("\n=== End Configuration Dump ===", DEBUG_BASIC, _plugin.debug_level)