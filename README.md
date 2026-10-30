# Luxtronik Heat Pump Controller Plugin for Domoticz

Monitor and control a Luxtronik heat pump from Domoticz, with efficiency numbers you can trust. The plugin reads Luxtronik 2.0/2.1 based controllers (used by Alpha Innotec, Siemens Novelan, Roth, Elco, Buderus, Nibe, Wolf Heiztechnik and others) over your local network, creates devices for temperatures, power, heat output, COP, compressor and refrigerant data, and lets you change the heat pump's modes and setpoints from Domoticz.

**Documentation: <https://rouzax.github.io/luxtronik-domoticz-plugin/>**

Also published on the [Domoticz Forum](https://forum.domoticz.com/viewtopic.php?p=44176).

## Features

- **COP you can trust:** separate COP for heating, hot water and combined, reported only while the compressor runs steadily.
- **Pump power compensation:** adds the estimated circulation and brine pump power to the compressor-only power reading, with presets for the Alpha Innotec WZSV models.
- **Refrigerant diagnostics:** superheat, pressures, condensing temperature, refrigerant lift, discharge headroom and compression ratio.
- **Run time per period:** compressor, heating, hot water and backup heater run time and compressor starts per day, week, month and year.
- **Health bars:** on Domoticz 2026.4 and newer, key cards show a green/amber/red bar from the controller's own limits and the manuals.
- **Safe controls:** modes and setpoints can be changed from Domoticz; every write is checked against a fixed allowlist.
- **Stable devices:** device IDs are tied to the hardware entry, and names you change are never overwritten.
- **Five languages:** English, Polish, Dutch, German and French.
- **Multi-instance:** one hardware entry per heat pump.
- **Update check:** a daily check announces new releases once; it sends nothing about you and can be turned off.

## Requirements

- Domoticz 2026.1 or newer (the settings page uses named plugin settings, which older versions do not have)
- A Luxtronik-based heat pump controller with network access (TCP port 8889 by default)
- Python 3.11 or newer

## Installation

Install into a folder named `luxtronikex` in the Domoticz `plugins` folder, using one of:

- **Release zip (recommended):** download `luxtronikex-vX.Y.Z.zip` from the [latest release](https://github.com/Rouzax/luxtronik-domoticz-plugin/releases/latest) and extract it in the `plugins` folder.
- **Git, with easy updates:**
  ```sh
  cd /path/to/domoticz/plugins
  git clone -b dist https://github.com/Rouzax/luxtronik-domoticz-plugin.git luxtronikex
  ```
  Update later with `git -C /path/to/domoticz/plugins/luxtronikex pull`.
- **Plugin manager:** the plugin is listed as `luxtronikex` in PyPluginStore and pp-manager.

Then restart Domoticz, go to **Setup → Hardware**, add **Luxtronik Heat Pump Controller v2**, and enter the IP address of your heat pump. Keep exactly one copy of the plugin in `plugins/`.

Full instructions, including switching install method: [Installation](https://rouzax.github.io/luxtronik-domoticz-plugin/install/).

> **Upgrading from 2.2.x or older?** The settings moved to new fields. Your previous values stay in use until you next save the plugin's hardware page, but that page shows the defaults, not your values. Choose your values again before pressing **Update**; the plugin lists them in the Domoticz log at every start until you do. See [Upgrading from 2.2.x or older](https://rouzax.github.io/luxtronik-domoticz-plugin/install/#upgrading-from-22x-or-older).

## Configuration

Only the IP address is needed for a working install. Two things are worth doing for accurate COP figures:

- Set **Pump power compensation** to your heat pump model, or Custom with your pump's values. See [Pump power compensation](https://rouzax.github.io/luxtronik-domoticz-plugin/settings/#pump-power-compensation).
- Enable **Setup → Settings → Log History → "Only add newly received values to the Log"** in Domoticz. See [COP accuracy](https://rouzax.github.io/luxtronik-domoticz-plugin/settings/#cop-accuracy).

Every setting is described on the [Settings](https://rouzax.github.io/luxtronik-domoticz-plugin/settings/) page.

## Documentation

- [Installation](https://rouzax.github.io/luxtronik-domoticz-plugin/install/)
- [Settings](https://rouzax.github.io/luxtronik-domoticz-plugin/settings/)
- [Devices](https://rouzax.github.io/luxtronik-domoticz-plugin/devices/): every device with its unit number
- [Migrating from v1](https://rouzax.github.io/luxtronik-domoticz-plugin/migration/): bring your history over from the original plugin
- [Troubleshooting / FAQ](https://rouzax.github.io/luxtronik-domoticz-plugin/faq/)
- [Security](https://rouzax.github.io/luxtronik-domoticz-plugin/security/)

## Development

### Files

| File | Purpose |
|------|---------|
| `plugin.py` | Settings manifest, Domoticz callbacks and the plugin lifecycle |
| `plugin_config.py` | Reads the hardware settings, including values left in the fields used by 2.2 and older |
| `domoticz_api.py` | The only module that calls Domoticz (logging, devices, stored state, notifications) |
| `connection.py` | Socket connection to the Luxtronik controller, with the write allowlist |
| `addresses.py` | Luxtronik protocol address constants and configuration limits |
| `device_specs_table.py` | The table of every device the plugin creates |
| `device_spec.py` | Device specification dataclasses |
| `device_factory.py` | Builds device specifications and converters |
| `converters.py` | Data converter classes (DataConverter hierarchy) |
| `device_update_tracker.py` | Decides when a device value is written to Domoticz |
| `name_ownership.py` | Tracks which device names the plugin wrote, so names you changed are kept |
| `translations.py` | Multi-language translations for device names and descriptions |
| `translation_manager.py` | Selects the language and looks up translations |
| `debug_logger.py` | Debug level handling for log output |
| `context.py` | Shared plugin context and state |
| `update_check.py` | Daily GitHub release check, shared with the author's other plugins |
| `README.md` | This documentation file |
| `migration/` | Migration tools for upgrading from legacy plugin |
| `migration/README.md` | Migration instructions |
| `migration/discover.sql` | Preview device mappings and data counts |
| `migration/migrate.sql` | Migrate historical data from legacy plugin |


### Development notes

- The plugin uses the DomoticzEx framework (`import DomoticzEx`)
- Every Domoticz call goes through `domoticz_api.py`, so the other modules can be tested without Domoticz
- Device Unit IDs are organized into 14 logical groups (see `build_device_specs()` in `device_specs_table.py`)
- Write operations require addresses to be in `available_writes` dictionary
- Gated converters check compressor frequency before reporting values (temperature difference converters also pass during passive cooling)
- Translations use `spec_id` as the lookup key
- `update_check.py` and `tests/test_update_check.py` are maintained in [home-connect-domoticz-plugin](https://github.com/Rouzax/home-connect-domoticz-plugin) and copied here unchanged; make changes there first

## Support

Building tools that solve my own problems and sharing them in the hope they solve yours too. This one saves you the evening of decoding raw Luxtronik registers by hand before your heat pump shows up in Domoticz.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/O0W221GBUG)

## License

MIT, see [LICENSE](LICENSE).

## Changelog

### Version 3.2.0
- Added: Units 186-192 show run time and compressor starts as Domoticz counters, so the card shows today's value and the log has bars per day, week, month and year: compressor, compressor starts, heating, hot water and backup heater run time (cooling and heat pump run time start unused). Run times are in minutes; on a Domoticz that lets plugins set a counter divider they are created in hours. See [Run time per day, week and month](https://rouzax.github.io/luxtronik-domoticz-plugin/devices/#run-time-per-day-week-and-month).
- Added: on Domoticz 2026.4 and newer, health bars on hot gas, supply temperature, hot water, superheat, the three COP devices and the last compressor cycle. Every edge comes from the controller's own limits (read live), the WZSV or Luxtronik manual, or Alpha Innotec. Bars you change yourself are kept. See [Health bars](https://rouzax.github.io/luxtronik-domoticz-plugin/devices/#health-bars).
- Docs: the plugin is licensed under MIT.

### Version 3.1.0
- Added: Unit 203 "Last fault" shows the controller's newest stored fault as code, message and time (for example "790: Severe inverter fault (2022-07-15 13:18)"), in Dutch, German, Polish or English (French uses English). A new fault is also written to the log and sent once through every Domoticz notification system. See [Fault codes](https://rouzax.github.io/luxtronik-domoticz-plugin/fault-codes/).
- Added: Unit 204 "Firmware" and Unit 205 "Heat pump type" (unused by default).
- Changed: Working mode shows all eight controller states. An EVU lock now shows "EVU" instead of "Cooling", and defrost, external heating and active cooling no longer show "No requirement".
- Fixed: with pump power compensation on, Working mode never showed "Idle" while the circulation pump ran; it now goes by the compressor's own power.
- Fixed: gated devices waited about 40 seconds instead of 2 minutes after the compressor reached steady speed; the wait is now measured in time.
- Fixed: Refrigerant lift (Unit 171) and Condensing-supply ΔT (Unit 172) updated during passive cooling, with the compressor off.
- Fixed: a selector level that does not exist (for example from a script) was turned into Automatic or a neighbouring mode and written to the heat pump; it is now refused. The Cooling switch only writes for an exact On or Off command.
- Fixed: when Domoticz refused new devices ("Accept new devices" off), the plugin still logged them as created; it now names them in one warning with how to allow them.
- Docs: a documentation site at https://rouzax.github.io/luxtronik-domoticz-plugin/, linked from the hardware page; repository links point to the renamed repository.

### Version 3.0.0
- Changed: the settings page is reorganised. Pump power compensation is chosen by heat pump model (WZSV 62, 92, 122, 162) with values from the WZSV manual, or Custom with four separate fields; Language defaults to "Same as Domoticz"; the update interval is a choice of 10, 15, 20 or 30 seconds (the maximum is now 30); invalid custom pump values are reported by field. Existing values keep working until the hardware page is next saved, and the plugin lists them in the log and in a one-time notification; choose them again before saving (see [Upgrading from 2.2.x or older](https://rouzax.github.io/luxtronik-domoticz-plugin/install/#upgrading-from-22x-or-older)).
- Added: daily update check with a new **Update check** setting (Automatic, Stable releases only, Including betas, Off); a newer release is announced once in the log and through every Domoticz notification system.
- Fixed: the description of Unit 202 "Cooling release" was English in every language; it is now translated, and existing devices pick it up on the next start unless you edited the description.
- Requires Domoticz 2026.1 or newer and Python 3.11 or newer.

### Version 2.2.0
- Manual device renames are now respected permanently: the plugin never overwrites a name you set, on restart or when the plugin language changes. Previously a rename could be reverted if it matched one of the plugin's translated names in another language.
- Changing the plugin language re-translates only the devices you have not customized. The same protection covers device descriptions and selector option labels, tracked per device. Existing installs migrate automatically on the first start after the upgrade.
- Internal: the plugin is split into focused modules behind a single Domoticz interface module, with type-checking and test-coverage gates. No change to device numbers, names, or values.

### Version 2.1.2
- Fixed: control commands (mode selectors, setpoints) could silently stop working after a plugin restart. The plugin no longer registers custom device classes, which failed to register on a reload; command handling now uses the standard module-level handler, so selector switches and setpoints reliably send their validated writes. This also removes the two "class registration failed" errors that appeared in the Domoticz log at startup. Existing devices are unaffected (no re-creation or renaming).

### Version 2.1.1
- Added `externallink` to the plugin definition (links to the GitHub repository from the Domoticz hardware page, and lets plugin managers reliably match the installed plugin to its repository)

### Version 2.1.0
- New compressor device: Unit 145 "Freq headroom" (target frequency minus actual Hz), shows remaining modulation headroom while the compressor runs
- Refrigerant circuit corrections and new diagnostic devices:
  - Unit 162 renamed to "Compressor heating temp" (LIN inverter/compressor-body heating sensor, calc 177)
  - Unit 164 renamed to "Condensing temperature" (controller's computed condensing/saturation temperature, calc 233)
  - Units 168 (Condensing temp), 169 (Subcooling), and 170 (Condensing pressure) retired: these addresses carried configuration setpoints and a firmware version, not live sensor values; subcooling is not measurable on this controller
  - New Unit 171 "Refrigerant lift" (K): condensing temp minus evaporating temp; the primary COP driver, gated
  - New Unit 172 "Condensing-supply ΔT" (K): signed condensing temp minus condenser leaving-water temp; positive = condenser headroom in low-temp heating, negative = desuperheat-dominated at high water temps (DHW), gated
  - New Unit 173 "Discharge headroom" (K): margin to the hot-gas trip setpoint; compressor health/margin-to-cutoff, gated
  - New Unit 174 "Compression ratio": high/low pressure ratio on absolute pressures; a rising trend flags refrigerant-circuit degradation, gated
- Plugin split into multiple modules: plugin.py, translations.py, addresses.py, context.py, converters.py

### Version 2.0.3
- Pump power compensation: estimates HUP/VBO circulation pump power from speed percentages and adds it to the compressor power reading for more accurate system COP
- Configurable pump power ranges with defaults for WZSV 92K3M
- New refrigerant diagnostics: condensing temperature, subcooling, condensing pressure (all gated, unused by default)
- New cooling release countdown timer (HH:MM:SS format, unused by default)
- Audit fixes for steady-state gating, refrigerant sensors, and robustness

### Version 2.0.2
- Temperature difference devices (heating ΔT, brine ΔT) now also update during passive cooling

### Version 2.0.1
- Single-connection refactor: heartbeat reads (READ_CALCUL + READ_PARAMS) now share one TCP connection instead of two separate connect/close cycles
- Configurable max COP limit to filter transient measurement spikes
- Fixed TCP partial read vulnerability in socket communication (`_recv_exact`)
- Fixed retry logic: MAX_RETRIES=1 actually meant zero retries (now MAX_ATTEMPTS=2)
- Clean up `_unit_specs` on plugin stop for consistent teardown
- Removed dead `onCommand` pass-through (DomoticzEx dispatches to Unit directly)

### Version 2.0.0
- **Breaking:** New plugin key `luxtronikex` (allows side-by-side installation with legacy)
- Complete refactor to DomoticzEx framework
- Multi-instance support with HardwareID-based device IDs (`luxtronikex_hw{id}`)
- Write protection with explicit address allowlist
- Steady-state gating for COP and pressure readings
- Intelligent device name updates preserving user customizations
- Heartbeat validation (clamped to 10-60 seconds)
- Added compressor runtime, start count, capacity utilization
- Added refrigerant temperatures (evaporating, condensing, discharge)
- Added spread target/actual devices for heating and source circuits
- COP logging setting check with user notification
- Enhanced debug levels (Basic, Device, Comms, Verbose)
- SQL migration scripts for historical data transfer
