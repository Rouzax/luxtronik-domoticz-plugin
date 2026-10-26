# Fault codes

When the heat pump controller detects a fault, it stores a code between 701 and 807. The plugin shows the newest one on the **Last fault** device (unit 203) and, when a new fault appears, writes it to the log and sends a notification. This page lists what each code means.

!!! warning "Not a repair guide"

    The causes below are a summary of the controller manual, to help you understand the message and talk to your installer. Faults that say *Installer* in the Reset column need a qualified installer. Do not open the heat pump yourself.

## How the Last fault device works

- It shows the controller's **newest stored fault** with its date and time, for example `790: Severe inverter fault (2022-07-15 13:18)`. The time is shown in the time zone of your Domoticz server.
- The fault **stays visible after it is cleared**; the controller keeps its fault memory until an installer clears it. "No faults" means the controller has none stored.
- The message follows the plugin language: Dutch, German, Polish and English have their own texts; French uses the English text.
- A code the plugin does not know shows as `<code>: Unknown fault`.
- The total number of stored faults is on the **Error count** device (unit 200, unused by default).

## Notifications

When the controller stores a **new** fault, the plugin writes an error line to the Domoticz log and sends one notification through every notification system set up in Domoticz (**Setup → Settings → Notifications**):

```
Heat pump fault 790: Severe inverter fault (2026-11-03 07:12)
```

Each fault is announced once, also across restarts. The fault that is already stored when the plugin first reads your controller (after installing or upgrading) is not announced.

## All codes

Reset: *Automatic* means the heat pump restarts by itself; *Automatic after a waiting time* means it restarts after a countdown shown on the controller; *Installer* means the fault must be acknowledged on the controller, usually by an installer. An empty cell means the manual gives no details for that code.

| Code | Message | Cause | Reset |
|------|---------|-------|-------|
| 701 | Error low pressure | Low-pressure switch/sensor tripped repeatedly (LW) or >20 s (SW) | Installer |
| 702 | Low pressure stop | L/W only: low pressure tripped, auto-restart | Automatic |
| 703 | Antifreeze | L/W only: flow temp <5 C while running, frost protection | Installer |
| 704 | Error hot gas | Max discharge-gas temp exceeded | Automatic after a waiting time |
| 705 | Motor protection VEN | L/W only: fan motor protection tripped | Installer |
| 706 | Motor protection BCP | B/W + W/W: brine/source pump or compressor motor protection | Installer |
| 707 | Coding of HP | Coding bridge break/short after first start | Installer |
| 708 | Return sensor | Return sensor break/short | Installer |
| 709 | Flow sensor | Flow sensor break/short | Installer |
| 710 | Hot gas sensor | Discharge-gas sensor break/short | Installer |
| 711 | External temp. sensor | Outdoor sensor break/short (fixed at -5 C) | Installer |
| 712 | Domestic hot water sensor | DHW sensor break/short | Installer |
| 713 | HS-on sensor | Heat-source-inlet sensor break/short | Installer |
| 714 | Hot gas DHW | Thermal use limit exceeded, DHW blocked | Automatic after a waiting time |
| 715 | High-pressure switch-off | High-pressure switch tripped, auto-restart | Automatic |
| 716 | High-pressure fault | High-pressure switch tripped multiple times | Installer |
| 717 | Flow rate HS | W/W flow switch tripped during prerinse/operation | Installer |
| 718 | Max. outside temp | L/W only: outdoor temp above max | Automatic after a waiting time |
| 719 | Min. outside temp | L/W only: outdoor temp below min | Automatic after a waiting time |
| 720 | HS temperature | B/W + W/W: evaporator-outlet temp below safety value | Automatic after a waiting time |
| 721 | Low-pressure switch-off | SW/WW: low-pressure switch tripped, auto-restart | Automatic |
| 722 | Tempdiff HW | Heating temp spread negative (faulty) | Installer |
| 723 | Tempdiff DHW | DHW temp spread negative (faulty) | Installer |
| 724 | Tempdiff defrosting | Heating spread >15 K during defrost (freeze risk) | Installer |
| 725 | System error DHW | DHW mode disturbed, temp far below setpoint | Installer |
| 726 | Sensor mixing circ 1 | Mixing-group sensor break/short | Installer |
| 727 | Brine pressure | Brine pressure switch tripped | Installer |
| 728 | Sensor HS Off | Heat-source-outlet sensor break/short | Installer |
| 729 | Rotating field error | Compressor running with no output (phase rotation) | Installer |
| 730 | Screed heating error | Warm-up program could not reach temp step in time | Installer |
| 731 | Timeout TDI |  |  |
| 732 | Cooling fault | Heating-water temp dropped below 16 C repeatedly | Installer |
| 733 | Anode fault | Parasitic-current anode fault input tripped | Installer |
| 734 | Anode fault | Fault 733 persists >2 weeks, DHW blocked | Installer |
| 735 | Error Ext. En | Comfort board: "external energy source" sensor break/short | Installer |
| 736 | Error solar collector | Comfort board: solar-collector sensor break/short | Installer |
| 737 | Error solar tank | Comfort board: solar-buffer sensor break/short | Installer |
| 738 | Error mixing circle 2 | Comfort board: mixing-group-2 sensor break/short | Installer |
| 739 | Error mixing circle 3 |  |  |
| 750 | Return sensor external | Return sensor break/short | Installer |
| 751 | Phase monitoring fault | Phase-sequence relay tripped |  |
| 752 | Flow error | Flow switch tripped (see 751 + 717) |  |
| 755 | Lost connection to slave | Slave silent >5 min | Installer |
| 756 | Lost connection to master | Master silent >5 min | Installer |
| 757 | Low-pressure fault in DHW heat pump | WW low-pressure switch tripped repeatedly/>20s; after 3x needs authorized service | Installer |
| 758 | Defrosting malfunction | Defrost ended 5x by too-low flow temp |  |
| 759 | TDI message | Thermal disinfection failed 5x in a row |  |
| 760 | Defrosting fault | Defrost ended 5x via max time (strong wind on evaporator) |  |
| 761 | LIN timeout/LIN-connection lost | LIN bus timeout (cable/contact) |  |
| 762 | sensor (evaporator intake) | Sensor Tu (evaporator suction) fault |  |
| 763 | sensor (compressor intake) | Sensor Tu1 (compressor suction) fault |  |
| 764 | Sensor Compressor heater | Compressor-heating sensor fault |  |
| 765 | Overheating | Superheat <2K for >5 min |  |
| 766 | compressor's functional range | Running 5 min outside compressor envelope (phase rotation) |  |
| 767 | STB E-Rod | Safety temp limiter of SEC heating element tripped |  |
| 768 | Flow monitoring | LW160H(A)V insufficient flow during defrost |  |
| 769 | Pump control | Too little flow after 10 s compressor run (PWM/pump) |  |
| 770 | Low superheat | Superheat below limit for long period |  |
| 771 | High superheat | Superheat above limit for long period |  |
| 776 | limit of application-CP | Compressor outside envelope for long period |  |
| 777 | Expansion valve | Expansion valve defect |  |
| 778 | Low pressure sensor | Low-pressure sensor defect |  |
| 779 | High pressure sensor | High-pressure sensor defect |  |
| 780 | EVI sensor | EVI sensor defect |  |
| 781 | Liquid temp. sensor before EXV | "liquid before expansion valve" sensor defect |  |
| 782 | Suction gas EVI temp. sensor | "EVI suction gas" sensor defect |  |
| 783 | Communication SEC - Inverter | SEC<->inverter communication disturbed |  |
| 784 | VSS lockdown | Inverter blocked; power down whole installation 2 min |  |
| 785 | SEC-Board defective | Fault detected in SEC board (replace) |  |
| 786 | Communication SEC - HZ/IO | SEC<->HZIO communication fault detected by SEC |  |
| 787 | VD alert | Compressor reports fault |  |
| 788 | Severe inverter fault | Fault in the inverter (check inverter) |  |
| 789 | LIN/Encoding not found | Control unit could not determine coding (LIN/coding resistor) |  |
| 790 | Severe inverter fault | Fault in inverter/compressor power supply (check wiring, inverter, compressor) |  |
| 791 | Lost ModBus communication | SEC board unreachable; HZIO found but no SEC board detected |  |
| 792 | LIN-connection lost | No main board / no configuration found |  |
| 793 | Severe inverter fault | Temperature fault in inverter (self-fixes) |  |
| 794 | Overvoltage | Overvoltage on inverter |  |
| 795 | Undervoltage | Undervoltage on inverter |  |
| 796 | Safety switch off | Safety input active: case 1 inverter fault, case 2 HP pressure switch in cooling circuit |  |
| 797 | MLRH is not supported | Heating-element control not supported |  |
| 798 | ModBus Fan | Modbus fault ventilator (auto reset) | Automatic |
| 799 | ModBus ASB | Modbus fault ASB board (auto reset) | Automatic |
| 800 | Desuperheater-error |  |  |
| 802 | Switchbox fan |  |  |
| 803 | Switchbox fan |  |  |
| 806 | ModBus SEC |  |  |
| 807 | Lost ModBus connection |  |  |
