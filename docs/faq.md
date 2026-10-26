# Troubleshooting / FAQ

Find the symptom you see, then check the likely causes in order. Most problems show a line in the Domoticz log (**Setup → Log**); raising the [Debug level](settings.md#debug-level) shows more.

## Cannot connect to the heat pump

The log shows:

```
Connection failed to 192.168.1.50:8889 (ConnectionRefusedError: [Errno 111] Connection refused)
```

or a timeout instead of "refused".

- **Wrong IP address.** Check the controller's address in its own menu or in your router, and compare it with the hardware page. A DHCP reservation keeps it from changing.
- **Wrong port.** The controller listens on `8889` unless someone changed it.
- **Not reachable from Domoticz.** From the Domoticz machine, run `nc -vz <ip-address> 8889`; it should report the port as open. If Domoticz runs in Docker, run the test from inside the container, and make sure the container can reach your LAN.
- **A firewall or VLAN rule** between Domoticz and the heat pump blocks TCP 8889.

The plugin retries on every update, so it recovers on its own once the connection works.

## A device is missing

- **It is an unused device.** 22 of the 68 devices start hidden. See [Enabling unused devices](devices.md#enabling-unused-devices); the [Devices](devices.md) page marks which ones.
- **You deleted it.** The plugin creates missing devices when it starts. Restart the plugin (press **Update** on its hardware page, or restart Domoticz) and the device comes back, under the same unit number, but without its old history.
- **Creation failed.** Look in the log right after the plugin starts for errors; set the debug level to **Basic** to see "Creating devices" and what follows.

## A device stays empty or never updates

- **It is gated.** Many devices only update while the compressor runs steadily, so they stay unchanged while the heat pump is idle. See [Gated devices](devices.md#gated-devices).
- **Your heat pump has no such sensor.** Devices such as the mixing circuits, flow or room temperature only show values if your installation has the matching sensor. Leave such devices unused.

## COP looks too high

- **Pump power compensation is off.** The controller only measures compressor power, so COP leaves out the circulation pumps. Set [Pump power compensation](settings.md#pump-power-compensation) to your model, or Custom.
- **You are looking at a mild period.** With a small temperature lift, for example low-temperature floor heating with a warm ground source, COP values of 6 or more are real.
- **Averages include idle time.** See the next item.

## COP averages look wrong, or COP keeps logging while the heat pump is idle

Domoticz repeats the last received value every 5 minutes by default, also while the heat pump is idle. Enable **Setup → Settings → Log History → "Only add newly received values to the Log"**. See [COP accuracy](settings.md#cop-accuracy). The plugin logs a "COP Warning" line at every start while this setting is off.

## COP never updates

- **The compressor has not run steadily for 2 minutes yet.** COP only updates after that.
- **COP heating and COP DHW only update in their own mode.** COP DHW stays unchanged during heating and the other way round.
- **No COP during passive cooling.**
- **The Max COP value filters the readings.** If real readings are above the [Max COP value](settings.md#max-cop-value), they are discarded; raise it, or set it to 0 to turn the filter off. With debug level **All**, the log names the reason for every skipped reading.

## Settings are back at defaults after upgrading

Since version 3.0.0 the settings live in new fields. If the hardware page was saved after the upgrade without choosing the values again, the defaults it showed were stored. Choose your values again and press **Update**.

If you still have the notification or log line from before that save ("Settings moved to new fields ... Previous values: ..."), it lists the values you had. See [Upgrading from 2.2.x or older](install.md#upgrading-from-22x-or-older).

## Device names did not change language

- **You renamed the device.** A name you changed yourself is kept in every language; that is deliberate.
- **The plugin has not restarted yet.** Names change when the plugin starts. Press **Update** on the hardware page.
- **Language is set to Same as Domoticz** and the Domoticz interface language is not English, Polish, Dutch, German or French. The plugin then uses English. Pick a language on the hardware page instead.

## Write commands do nothing

Changing a mode or setpoint has no effect, and the log shows a line starting with `WRITE BLOCKED`:

- **Only the control devices (units 10-16) can write to the heat pump.** Commands sent to any other device are refused on purpose. See [Security](security.md#what-the-plugin-can-change-on-the-heat-pump).
- **The value is outside the device's range**, for example a DHW target above 65 °C sent by a script. Use a value the device offers.

If there is no `WRITE BLOCKED` line, set the debug level to **Basic + Comms** and try again; the log then shows whether the command reached the heat pump.

## What to include in a bug report

Open an [issue on GitHub](https://github.com/Rouzax/luxtronik-domoticz-plugin/issues) with:

1. The plugin version (the release you installed, or `version=` near the top of `plugin.py`) and your Domoticz version.
2. Your heat pump model.
3. What you expected and what happened instead.
4. Log lines: set the debug level to **All**, wait for two or three update cycles, copy the plugin's lines from the log, then set the debug level back to **None**.

Before posting, replace your IP addresses and any names you do not want public with placeholders.
