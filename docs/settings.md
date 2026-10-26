# Settings

All settings are on the plugin's hardware page (**Setup → Hardware**, select the plugin's entry). After changing one, press **Update**; the plugin restarts with the new values.

Only the IP address is needed for a working install. If you have an Alpha Innotec WZSV, also set **Pump power compensation**.

## Overview

| Setting | What it does | Default |
|---------|--------------|---------|
| IP address | IP address of the Luxtronik controller | `127.0.0.1` |
| Port | TCP port of the controller; `8889` unless you changed it on the controller | `8889` |
| Language | Language of the device names; see [Language](#language) | Same as Domoticz |
| Update interval | How often the heat pump is read: 10, 15, 20 or 30 seconds | 20 seconds |
| Pump power compensation | Adds estimated circulation pump power to the power reading; see [Pump power compensation](#pump-power-compensation) | Off |
| Heating pump min / max (W), Brine pump min / max (W) | Pump power ranges, shown only when Pump power compensation is **Custom** | `2` / `60`, `3` / `140` |
| Max COP value | COP readings above this are discarded; see [Max COP value](#max-cop-value) | `30` |
| Update check | Daily check for a newer release; see [Update check](#update-check) | Automatic |
| Debug level | Extra logging for troubleshooting; see [Debug level](#debug-level) | None |

## Language

Sets the language of device names, descriptions and selector options: English, Polski, Nederlands, Deutsch or Français.

- **Same as Domoticz** uses the Domoticz interface language when it is one of these five, and English otherwise.
- Changing the language renames the devices on the next start. A device you renamed yourself keeps your name, in every language.

## Update interval

How often the plugin reads the heat pump: every 10, 15, 20 or 30 seconds. The default of 20 seconds suits most installs. A shorter interval gives smoother graphs but more database writes; the controller itself is not affected.

Devices only send a new value to Domoticz when it changed, and graph devices repeat their value about every 2 minutes when it did not, so the interval has little effect on database size.

## Pump power compensation

The controller's power reading measures the **compressor only**. The heating circulation pump (HUP) and the brine pump (VBO) also use electricity, so a COP based on compressor power alone looks better than the system really performs.

With compensation on, the plugin estimates each pump's power from its current speed and adds it to the power reading. All power and COP devices then use the corrected value.

| Option | Heating pump (HUP) | Brine pump (VBO) |
|--------|--------------------|------------------|
| Off | not added | not added |
| WZSV 62 | 2 to 60 W | 5 to 87 W |
| WZSV 92 | 2 to 60 W | 3 to 140 W |
| WZSV 122 | 2 to 60 W | 3 to 180 W |
| WZSV 162 | 2 to 60 W | 3 to 180 W |
| Custom | the values you enter | the values you enter |

The model values come from the technical data in the Alpha Innotec WZSV installation manual and apply to the variants with and without cooling.

**Choose Custom** for another heat pump, or after a pump was replaced. Four fields appear; enter each pump's minimum and maximum power in watts from its data sheet or type plate.

??? note "How the estimate works"

    For each pump the plugin takes its speed (0 to 100 %) and calculates `min + (max - min) × speed²`. A stopped pump counts as 0 W. The squared curve sits between a linear estimate, which overestimates modern pumps, and the theoretical cubic pump law, which underestimates them.

**If a Custom value is wrong** (not a number, negative, or a minimum above its maximum), compensation stays off and the Domoticz log names the field, for example:

```
Pump power compensation off: Brine pump min 200 W is above max 140 W (values '2,60,200,140'). Correct them on the hardware page.
```

## Max COP value

COP readings above this value are thrown away as measurement artifacts, such as a short spike when the heat output reading jumps before the power reading. The default of 30 is far above any real COP, so it only catches nonsense values.

Set it to `0` or leave it empty to turn the filter off. A value that is not a number also turns it off, with a warning in the log.

## COP accuracy

The plugin reports COP only while the compressor runs steadily:

- The compressor must run at or above the controller's minimum target frequency, after a short settling period of up to 2 minutes. Start-up, ramp-up and idle periods are skipped.
- No COP is reported during passive cooling, where the compressor does not run.
- Readings below 10 W power or 100 W heat output are treated as noise.
- **COP heating** only updates in heating mode, **COP DHW** only in hot water mode.

That keeps the plugin from sending idle values. Domoticz itself still fills the log every 5 minutes with the last received value unless you change one setting:

!!! tip "Recommended Domoticz setting"

    **Setup → Settings → Log History → "Only add newly received values to the Log"**

    With it off (the Domoticz default), the last COP keeps being logged while the heat pump is idle, which skews daily and monthly COP averages. With it on, only real readings are logged.

    This is a system-wide setting: it affects every device in Domoticz, not just this plugin. While it is off, the plugin logs a "COP Warning" line at every start as a reminder.

For a true system COP, also set [Pump power compensation](#pump-power-compensation).

## Update check

Once a day the plugin asks GitHub for its list of releases. The first check runs 5 minutes after the plugin starts. When a newer version exists, the plugin:

- writes one line to the Domoticz log, with a link to the release page:
  ```
  Update available: version X.Y.Z (running A.B.C). Release notes and download: https://github.com/...
  ```
- sends one notification through every notification system configured in Domoticz (**Setup → Settings → Notifications**).

Each version is announced once; the plugin remembers this across restarts. The check never installs anything.

| Option | What is reported |
|--------|------------------|
| Automatic | Betas while you run a beta, only stable releases while you run a stable one |
| Stable releases only | Stable releases |
| Including betas | Stable releases and betas |
| Off | Nothing; GitHub is never contacted |

The request to GitHub contains no information about you, your Domoticz or your heat pump; see [Security](security.md#update-check). If GitHub cannot be reached, the plugin tries again a day later and logs the failure only at a debug level that includes Comms.

## Debug level

For normal use, leave this at **None**: you then only see errors, warnings and a few important notices. Raise it while troubleshooting, and set it back afterwards; the higher levels fill the log quickly.

| Option | Adds to the log |
|--------|-----------------|
| None | Nothing extra |
| Basic | Start-up, connection status and a summary after each update ("Updated 7, unchanged 46, gated 2") |
| Basic + Device | Basic, plus every device update and what changed |
| Basic + Comms | Basic, plus connection handling and protocol messages |
| Basic + Device + Comms | All of the above |
| All | Everything, including why a gated device was skipped, value conversion details, and Domoticz's own device and connection debug messages |

For a bug report, use **All** for a few update cycles; see [What to include in a bug report](faq.md#what-to-include-in-a-bug-report).
