# Luxtronik Heat Pump Controller Plugin for Domoticz

## Overview

This plugin is based on the incredible work of [ajarzyn](https://github.com/ajarzyn/domoticz-luxtronic2).
This plugin allows Domoticz to communicate with Luxtronik-based heat pump controllers via socket communication. It enables real-time monitoring of heat pump parameters, including temperature readings, operating modes, and power consumption.

## Features

- Real-time monitoring of heat pump parameters
- Support for temperature readings, operating modes, and power consumption
- Multi-language support (English, Polish, Dutch)
- Configurable update intervals
- Debug logging for troubleshooting

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
| Language        | Interface language (English, Polish, Dutch)          | `English`     |
| Debug Level     | Debug log level for troubleshooting                  | `None`        |

## Created Devices

The plugin creates the following devices in Domoticz:

- **Temperature Sensors:**

  - Heat supply temperature
  - Heat return temperature
  - Outside temperature
  - Domestic hot water (DHW) temperature
  - Room temperature

- **Power Consumption:**

  - Total power consumption
  - Power consumption for heating mode
  - Power consumption for DHW mode

- **Operating Modes:**

  - Heating mode
  - Hot water mode
  - Cooling mode

- **Flow and Frequency:**

  - Flow rate sensor
  - Compressor frequency

- **Performance Indicators:**

  - Coefficient of Performance (COP)
  - Heat output for heating and DHW

## Debugging

If needed, you can enable different levels of debugging:

- Basic
- Basic + Device
- Basic + Connection
- Basic + Protocol
- Basic + Data Processing
- All

These can be adjusted in the plugin settings within Domoticz.

## Troubleshooting

- Ensure the Luxtronik controller is reachable from the Domoticz server.
- Verify the correct IP address and port are entered in the plugin configuration.
- Check the Domoticz logs (`Setup` > `Log`) for any error messages.

## Contributing

Contributions are welcome! If you find any issues or have feature requests, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

