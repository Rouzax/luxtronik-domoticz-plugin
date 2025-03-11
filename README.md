# Luxtronik Heat Pump Controller Plugin for Domoticz

## Overview

The Luxtronik plugin for Domoticz provides seamless socket communication with Luxtronik-based heat pump controllers. Building on the work of [ajarzyn](https://github.com/ajarzyn/domoticz-luxtronic2), this version brings enhanced features including granular debug logging, robust device update tracking, and advanced multi-language support (English, Polish, Dutch, German and French). The plugin enables real-time monitoring and control of various heat pump parameters while optimizing network communications with retry logic and smart update intervals.

## Features

- **Real-Time Monitoring:**  
  Retrieve live data from heat pump sensors such as temperature, pressure, power consumption, and more.
  
- **Comprehensive Device Support:**  
  Automatically create and update devices for temperature sensors, pressure readings, pump speeds, operating modes, flow rates, and energy metrics including COP (Coefficient of Performance).

- **Advanced Update Mechanism:**  
  Uses a dedicated update tracker to compare current values against new readings. Graphing devices will only resend their value at set intervals (every 5 minutes) when sensor values remains constant, changes are sent immediately ensuring accurate long-term trend analysis.

- **Granular Debug Logging:**  
  Multiple debug levels are available for troubleshooting, including:
  - **Basic:** Plugin startup and configuration details.
  - **Device:** Device update and state change information.
  - **Connection:** Connection handling details.
  - **Protocol:** Detailed socket communication and protocol messages.
  - **Data Processing:** Information on data parsing and conversion.
  - **All:** Enables all debugging categories.

- **Configurable Update Interval:**  
  The heartbeat interval can be set (recommended between 15–30 seconds). Note that values greater than 30 seconds may trigger a Domoticz timeout warning, though the plugin continues to operate correctly.

- **Multi-Language Support:**  
  Available languages include English, Polish, Dutch, German and French.

- **Robust Socket Communication:**  
  Implements retry logic and verification of command echoes for reliable communication with the heat pump controller.

- **Command & Control:**  
  Supports both read and write operations (via `READ_PARAMS`, `READ_CALCUL`, `WRIT_PARAMS`, etc.) for controlling operating modes and parameter settings.

## Requirements

- Domoticz home automation system
- A Luxtronik-based heat pump controller with network access

## Installation

1. **Navigate to the Domoticz plugins directory**:
   ```sh
   cd /path/to/domoticz/plugins
   ```
2. **Clone the repository**:
   ```sh
   git clone https://github.com/Rouzax/luxtronik-domoticz-plugin.git
   ```
3. **Restart Domoticz**:
   ```sh
   sudo systemctl restart domoticz.service
   ```
4. **Enable the plugin**:
   - In Domoticz, navigate to `Setup` > `Hardware`
   - Add a new hardware device and select `Luxtronik Heat Pump Controller`
   - Enter the necessary configuration details
   - Click `Add`

## Configuration

The following parameters are required to configure the plugin:

| Parameter       | Description                                          | Default Value |
| --------------- | ---------------------------------------------------- | ------------- |
| Address         | IP address of the Luxtronik controller               | `127.0.0.1`   |
| Port            | TCP port of the controller (default: 8889)           | `8889`        |
| Update Interval | Data update interval in seconds (recommended: 15-30) | `20`          |
| Language        | Interface language (English, Polish, Dutch, French, German)          | `English`     |
| Debug Level     | Debug log level for troubleshooting                  | `None`        |

## Created Devices

The plugin automatically creates or updates the following devices in Domoticz based on real-time readings from your Luxtronik controller:

- **Temperature Sensors:**
  - **Heat Supply Temperature:** Monitors the temperature of the heat supply (flow) line.
  - **Heat Return Temperature:** Monitors the temperature of the return line.
  - **Return Temperature Target:** The calculated target return temperature.
  - **Outside Temperature:** Current ambient outdoor temperature.
  - **Outside Temperature Average:** An average of the outdoor temperature over time.
  - **Domestic Hot Water (DHW) Temperature:** Current temperature of the domestic hot water.
  - **DHW Target Temperature:** The set target temperature for domestic hot water.
  - **Source Inlet Temperature:** Temperature at the water source inlet (e.g., ground or well).
  - **Source Outlet Temperature:** Temperature at the water source outlet.
  - **Mixing Circuit 1 Temperature:** Current and target temperatures for the first mixing circuit.
  - **Mixing Circuit 2 Temperature:** Current and target temperatures for the second mixing circuit.
  - **Room Temperature:** Current room temperature reading.
  - **Room Temperature Setpoint:** Desired room temperature target.
  - **Hot Gas Temperature:** Monitors the temperature of the hot gas.
  - **Compressor Suction Temperature:** Measures the suction temperature at the compressor.

- **Pressure & Refrigerant:**
  - **High Pressure:** Pressure measurement in the high-pressure circuit (in bar).
  - **Low Pressure:** Pressure measurement in the low-pressure circuit (in bar).
  - **Superheat:** Monitoring of the superheat value (in Kelvin).

- **Pump & Circulation:**
  - **Heating Circulation Pump Speed:** The speed percentage of the heating circulation pump.
  - **Brine/Well Pump Speed:** The speed percentage of the brine (or well) pump.

- **Power & Energy:**
  - **Total Electrical Power Consumption:** Overall power consumption (displayed in kWh).
  - **Heating Mode Power Consumption:** Power used when operating in heating mode.
  - **Domestic Hot Water (DHW) Power Consumption:** Power consumption in DHW mode.
  - **Total Heat Output:** Total heat output power.
  - **Heating Mode Heat Output:** Heat output when in heating mode.
  - **Domestic Hot Water Heat Output:** Heat output when in DHW mode.
  - **Overall System COP:** The coefficient of performance calculated for the system.

- **Operating Modes & Controls:**
  - **Heating Mode Selector:** A selector switch to control or display the heating mode.  
    *Options:* Automatic, 2nd heat source, Party, Holidays, Off.
  - **Hot Water Mode Selector:** A selector switch for the hot water operating mode.  
    *Options:* Automatic, 2nd heat source, Party, Holidays, Off.
  - **Cooling Mode Switch:** A switch to enable or disable the cooling mode.
  - **Working Mode Status:** Displays the current operating mode status as text.
  - **Temperature Offset Adjustment:** Allows fine-tuning of temperature settings.
  - **DHW Power Mode Selector:** A selector switch to control the DHW inverter mode.  
    *Options:* Normal and Luxury.

- **System Metrics:**
  - **Flow Rate:** Measures the system’s flow rate (in liters per hour).
  - **Compressor Frequency:** Monitors the compressor’s operating frequency (in Hz).
  - **Brine Temperature Difference:** Calculates the temperature difference between the source inlet and outlet.
  - **Heating Temperature Difference:** Calculates the difference between supply and return temperatures.


## Debugging

For effective troubleshooting, enable and adjust debug levels through the plugin settings:

- **Basic:** General startup and configuration information.
- **Basic + Device:** Detailed device state and update comparisons.
- **Basic + Connection:** Information on socket connection attempts and failures.
- **Basic + Protocol:** Low-level protocol messages and command verification.
- **Basic + Data Processing:** Data parsing and conversion details.
- **All:** Activates all debugging categories for complete traceability.

These settings can be found in the plugin configuration under **Debug Level**.

## Troubleshooting

- **Connection Issues:**  
  Ensure that the Luxtronik controller is reachable from your Domoticz server and that the correct IP address and port are configured.
  
- **Timeout Warnings:**  
  If the update interval is set above 30 seconds, Domoticz might show timeout warnings. This is expected and does not affect functionality.
  
- **Device Updates:**  
  Check the Domoticz logs (`Setup > Log`) for any errors related to device creation or updates. The plugin’s smart update tracker logs detailed messages to help diagnose any discrepancies.

- **Translations:**  
  If you notice untranslated texts, verify the selected language and review the Translation Manager logs for any missing translation keys.

## Contributing

Contributions are welcome! If you find any issues or have feature requests, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
