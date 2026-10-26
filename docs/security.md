# Security

What the plugin can change on your heat pump, what it sends over the network, and how to keep the connection safe.

## What the plugin can change on the heat pump

The plugin reads everything, but writes only the settings behind its control devices, and only within the ranges those devices offer:

| Unit | Device | What you can set |
|------|--------|------------------|
| 10 | Heating mode | Automatic, 2nd heat source, Party, Holidays, Off |
| 11 | Hot water mode | Automatic, 2nd heat source, Party, Holidays, Off |
| 12 | DHW Power Mode | Normal, Luxury |
| 13 | Cooling | On or off |
| 14 | Temp adjust | Heating curve offset, -5 to +5 °C in 0.5 °C steps |
| 15 | DHW temp target | Hot water setpoint, 30 to 65 °C in 0.5 °C steps |
| 16 | Room temp setpoint | 15 to 30 °C in 0.5 °C steps |

Every write is checked before anything is sent: the device must be one of the control devices above, the controller address it writes to must be on the plugin's fixed list of allowed addresses, and the value must be one that setting allows. Commands to other devices are ignored, and a refused address or setpoint value is logged with a line starting with `WRITE BLOCKED`, for example:

```
WRITE BLOCKED: Address 1234 not in allowed list
```

The list is part of the plugin's code, not a setting, so nothing on the hardware page or in Domoticz can widen it. This protects the controller's configuration memory from accidental writes, for example by a script that sends a command to the wrong device.

A mode selector (units 10-12) only accepts its own levels (0, 10, 20 and so on). A level it does not have, for example a wrong value sent by a script, is refused and logged with `WRITE BLOCKED`; nothing is sent to the heat pump.

!!! note

    Anyone who can operate these devices in Domoticz can change these heat pump settings. Use Domoticz user rights if other people or integrations have access to your Domoticz.

## The connection to the heat pump

The plugin talks to the controller over plain TCP on port 8889, the protocol the Luxtronik controller offers. It has **no encryption and no password**; this is a limit of the controller, not of the plugin.

- Keep the heat pump on a trusted network segment, ideally a separate VLAN for building equipment.
- Never forward port 8889 (or the controller's web interface) to the internet.
- For remote access, use a VPN into your home network instead.

## Update check

With **Update check** on (the default is Automatic), the plugin sends one request a day to GitHub's public API, `api.github.com`, for the list of releases of this plugin.

- The request carries the plugin's own version in its User-Agent header (`luxtronikex/<version> update-check`), because GitHub requires one. As with any web request, GitHub also sees the public IP address of your network.
- It sends nothing about you, your Domoticz, your devices or your heat pump, and uses no account or token.
- It downloads only the release list. The plugin never installs or changes anything itself.

Set **Update check** to **Off** to stop the requests entirely. See [Settings](settings.md#update-check) for the options.

## Reporting a security problem

If you find a security problem in the plugin, please report it privately through GitHub's [private vulnerability reporting](https://github.com/Rouzax/luxtronik-domoticz-plugin/security/advisories/new) instead of opening a public issue.
