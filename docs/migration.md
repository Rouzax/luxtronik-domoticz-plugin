# Migrating from v1

Coming from the original Luxtronik plugin (plugin key `luxtronik`)? Two SQL scripts copy your history (temperature graphs, energy meters, percentages and switch logs) onto the devices of this plugin, so your graphs continue where they left off.

The two plugins use different keys (`luxtronik` and `luxtronikex`), so they can run side by side while you migrate.

## Before you start

- **Both plugins installed and running**, each with its own hardware entry:
    - the old plugin, typically in `plugins/luxtronik-domoticz-plugin/` (key `luxtronik`)
    - this plugin in `plugins/luxtronikex/` (key `luxtronikex`), see [Installation](install.md)
- **Only one hardware entry of each.** The scripts find both plugins by their key and take one entry of each. With more than one heat pump they cannot tell which old entry belongs to which new one, so do not run them on such a setup.
- **`sqlite3`** on the Domoticz machine (`sudo apt install sqlite3` on Debian or Ubuntu).
- **The `migration/` folder.** It is not in the release zip or on the `dist` branch. Download [`discover.sql`](https://github.com/Rouzax/luxtronik-domoticz-plugin/blob/main/migration/discover.sql) and [`migrate.sql`](https://github.com/Rouzax/luxtronik-domoticz-plugin/blob/main/migration/migrate.sql) from the `main` branch into a `migration/` folder next to `domoticz.db`. The commands below run from the folder that holds `domoticz.db`.

!!! danger "Back up first"

    The migration writes directly into the Domoticz database. There is no undo other than restoring your backup.

## Steps

### 1. Back up the database

```bash
sudo systemctl stop domoticz
cp domoticz.db domoticz.db.backup
sudo systemctl start domoticz
```

### 2. Let the new plugin create its devices

Add this plugin as hardware (**Setup → Hardware**) with a temporary name such as `HPNEW`, and let it run for a few minutes so all devices exist.

### 3. Preview (optional)

```bash
sqlite3 domoticz.db < migration/discover.sql
```

This only reads. It shows which hardware entries were found, how old and new devices pair up, and how much history each has.

### 4. Migrate

```bash
sudo systemctl stop domoticz
sqlite3 domoticz.db < migration/migrate.sql
sudo systemctl start domoticz
```

### 5. Check and clean up

1. Open the graphs of a few new devices (a temperature, a kWh meter, a COP device) and check that the older history is there.
2. Disable or delete the old plugin's hardware entry, and remove its plugin folder.
3. Rename the new hardware entry to the name you want (for example `HP`).

If something looks wrong, stop Domoticz, put `domoticz.db.backup` back as `domoticz.db`, and start Domoticz again.

## What gets migrated

- **Temperatures:** all sensor history and daily aggregates.
- **Energy meters (kWh):** consumption and production history. Cumulative counters are carried over, so Today, Week and Month totals continue seamlessly.
- **Percentages and custom sensors:** pump speeds, COP values and similar.
- **Switches and selectors:** state change history.
- **Hourly statistics** used for usage patterns.

## How it works

- Devices are paired by **unit number**, not by name, so your language setting does not matter.
- Only history **older than** each new device's first value is copied, so nothing is duplicated.
- Values the new devices logged before the migration are tidied up so graphs join cleanly.

### Unit mapping

| Old unit | New unit | Type | Device |
|:--------:|:--------:|------|--------|
| 1 | 60 | Temperature | Heat supply temp |
| 2 | 61 | Temperature | Heat return temp |
| 3 | 62 | Temperature | Return temp target |
| 4 | 90 | Temperature | Outside temp |
| 5 | 91 | Temperature | Outside temp avg |
| 6 | 80 | Temperature | DHW temp |
| 7 | 15 | Setpoint | DHW temp target |
| 8 | 100 | Temperature | Source inlet temp |
| 9 | 101 | Temperature | Source outlet temp |
| 10 | 120 | Temperature | Circuit 1 temp |
| 11 | 121 | Temperature | Circuit 1 target |
| 12 | 130 | Temperature | Circuit 2 temp |
| 13 | 131 | Temperature | Circuit 2 target |
| 14 | 10 | Selector | Heating mode |
| 15 | 11 | Selector | Hot water mode |
| 16 | 13 | Switch | Cooling |
| 17 | 14 | Setpoint | Temp adjust |
| 18 | 1 | Text | Working mode |
| 19 | 106 | Custom | Source flow |
| 20 | 140 | Custom | Compressor freq |
| 21 | 92 | Temperature | Room temp |
| 22 | 93 | Temperature | Room temp target |
| 23 | 30 | kWh | Power total |
| 24 | 31 | kWh | Power heating |
| 25 | 32 | kWh | Power DHW |
| 26 | 40 | kWh | Heat out total |
| 27 | 41 | kWh | Heat out heating |
| 28 | 42 | kWh | Heat out DHW |
| 29 | 50 | Custom | COP total |
| 30 | 66 | Percentage | Heating pump |
| 31 | 105 | Percentage | Source pump |
| 32 | 160 | Temperature | Hot gas temp |
| 33 | 161 | Temperature | Suction temp |
| 34 | 165 | Custom | Superheat |
| 35 | 166 | Custom | Pressure high |
| 36 | 167 | Custom | Pressure low |
| 37 | 102 | Custom | Source ΔT |
| 38 | 63 | Custom | Heating ΔT |
| 39 | 12 | Selector | DHW Power Mode |
| 40 | 16 | Setpoint | Room temp setpoint |
| 41 | 51 | Custom | COP heating |
| 42 | 52 | Custom | COP DHW |
