# Installation

Install the plugin into Domoticz, add it as hardware, and check that the devices appear. This takes about five minutes.

## Before you start

- Domoticz **2026.1 or newer**, with Python 3.11 or newer. On an older Domoticz, stay on plugin version 2.2.0.
- The IP address of your heat pump controller, and the controller reachable from the Domoticz machine on TCP port **8889**. Giving the heat pump a fixed IP address (a DHCP reservation in your router) saves you from editing the hardware entry later.
- Shell access to the Domoticz machine, or a plugin manager that is already installed in Domoticz.
- If you are coming from the original Luxtronik plugin (key `luxtronik`): you can install this plugin next to it. Read [Migrating from v1](migration.md) first if you want to keep your history.

## Step 1: Put the plugin in place

All methods install into a folder named `luxtronikex` inside the Domoticz `plugins` folder. The name matches the plugin key; your devices do not depend on it, but using it keeps every method interchangeable.

=== "Release zip (recommended)"

    No git needed. The zip contains only the files Domoticz runs.

    1. Download `luxtronikex-vX.Y.Z.zip` from the [latest release](https://github.com/Rouzax/luxtronik-domoticz-plugin/releases/latest).
    2. Extract it in the Domoticz `plugins` folder. The zip already contains the `luxtronikex` folder:

        ```sh
        cd /path/to/domoticz/plugins
        unzip ~/Downloads/luxtronikex-vX.Y.Z.zip
        ```

    To update, extract the newer zip over the same folder.

=== "Git (dist branch)"

    The `dist` branch holds only the files Domoticz runs and is updated with every release, so you can update with `git pull`.

    ```sh
    cd /path/to/domoticz/plugins
    git clone -b dist https://github.com/Rouzax/luxtronik-domoticz-plugin.git luxtronikex
    ```

    To update:

    ```sh
    git -C /path/to/domoticz/plugins/luxtronikex pull
    ```

=== "Plugin manager"

    The plugin is listed as **luxtronikex** in PyPluginStore and in pp-manager. Install it from there; both install the lean runtime files into `plugins/luxtronikex`.

    An install made with an older manager entry stays on the branch it was cloned from. Uninstall and reinstall it through the manager to move to the current one.

=== "Full repository (developers)"

    Clones everything, including tests and these docs. Use this only if you want to work on the plugin.

    ```sh
    cd /path/to/domoticz/plugins
    git clone https://github.com/Rouzax/luxtronik-domoticz-plugin.git luxtronikex
    ```

!!! warning "Keep exactly one copy"

    Domoticz loads every `plugins/*/plugin.py` it finds. Two folders that both contain this plugin register it twice. When you switch install method, **replace** the old folder; do not add a second one.

## Step 2: Restart Domoticz

```sh
sudo systemctl restart domoticz.service
```

Domoticz only picks up new or updated plugins when it starts. (On Docker, restart the container instead.)

## Step 3: Add the hardware

1. In Domoticz, go to **Setup → Hardware**.
2. Choose **Luxtronik Heat Pump Controller v2** as the type and give it a name, for example `HP`. The name becomes the prefix of every device name ("HP - Outside temp").
3. Enter the **IP address** of the heat pump controller. Leave the port at `8889` unless you changed it on the controller.
4. If you have an Alpha Innotec WZSV, set **Pump power compensation** to your model for a more accurate COP. The other settings work as they are; see [Settings](settings.md) for what each does.
5. Click **Add**.

## Step 4: Check that it works

The plugin creates its devices on the first start. Within a minute:

- **Setup → Devices** lists the new devices, filtered by your hardware name. Most are active; a few start as unused (see [Devices](devices.md#enabling-unused-devices)).
- The temperature, utility and switch tabs show the devices with live values.
- The Domoticz log shows no errors from the plugin.

You may see this line in the log at every start:

```
COP Warning: For accurate COP averages, enable Settings → Log History → 'Only add newly received values to the Log'. Currently disabled - stale values will be logged during idle periods.
```

It is advice, not an error. [COP accuracy](settings.md#cop-accuracy) explains why the setting matters and what else it affects.

If devices do not appear or stay empty, see [Troubleshooting](faq.md).

## Switching install method

Your devices and their history belong to the hardware entry in Domoticz (the device ID is `luxtronikex_hw<HardwareID>`), not to the plugin folder. You can change folder or install method without losing anything, as long as you keep the same hardware entry.

To switch, for example from a full clone to the `dist` branch:

1. Stop Domoticz.
2. Delete the old plugin folder.
3. Install again with the method you want, into `plugins/luxtronikex`.
4. Start Domoticz. The hardware entry and all devices come back unchanged.

## Upgrading from 2.2.x or older

Version 3.0.0 moved the settings to new fields on the hardware page.

- Your previous values **stay in use** until you next save the hardware page.
- The hardware page shows the **defaults**, not your values. Pressing **Update** without choosing your values again resets them to those defaults.
- Until you save, the plugin lists your previous values in the Domoticz log at every start ("Settings moved to new fields ... Previous values: ..."), and sends the same list once through your Domoticz notification systems.
- IP address and port are not affected.
- An update interval above 30 seconds is now limited to 30 seconds. An interval that is not one of the choices keeps running until you pick the nearest one.

So: before pressing **Update** on the hardware page, look up your previous values in the log and choose them again.
