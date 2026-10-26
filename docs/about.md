# About

## Why this plugin exists

This is a rewrite of the original Luxtronik plugin for Domoticz, built on Domoticz's newer plugin framework (DomoticzEx). The original worked, but had limits that could not be fixed without starting over:

- a limit of 256 devices per plugin;
- device IDs that could change, leaving orphaned devices and broken history;
- COP values logged while the heat pump was idle, which dragged efficiency statistics down;
- no way to monitor more than one heat pump.

This plugin fixes all four, and adds what a heat pump owner actually wants to know: an honest COP, pump power compensation, and diagnostics that show a refrigerant circuit drifting long before it fails.

It is developed and tested on an Alpha Innotec WZSV ground-source heat pump, with low-temperature floor heating and cooling.

## Changes between versions

Each release on GitHub lists what changed: see [Releases](https://github.com/Rouzax/luxtronik-domoticz-plugin/releases). The README in the plugin folder carries the same changelog.

## Getting help and contributing

- Questions, problems and ideas: open an [issue on GitHub](https://github.com/Rouzax/luxtronik-domoticz-plugin/issues), or reply in the plugin's thread on the [Domoticz forum](https://forum.domoticz.com/viewtopic.php?p=44176).
- Found a mistake in these pages? Every page has an edit button at the top that opens it on GitHub.
- Security problems: see [Reporting a security problem](security.md#reporting-a-security-problem).

## Support the project

Building tools that solve my own problems and sharing them in the hope they solve yours too. This one saves you the evening of decoding raw Luxtronik registers by hand before your heat pump shows up in Domoticz.

If it is useful to you, you can [buy me a coffee on Ko-fi](https://ko-fi.com/O0W221GBUG).

*Not affiliated with Alpha Innotec or any heat pump manufacturer. Product names are trademarks of their owners.*
