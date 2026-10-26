"""Luxtronik fault codes and heat pump type codes, decoded for display.

Read-only lookup tables; nothing here talks to the heat pump.

Fault messages (calc[100], the controller's newest stored fault):
  - Dutch: the Luxtronik controller manual, part 2 (83055400cNL), fault table.
  - English, German, Polish: BenPru/luxtronik, custom_components/luxtronik2/translations,
    entity.sensor.error_reason.state, first line of each text. Corrected where they
    contradict the manual: the inverter faults 788/790/793 ("VSS" in en/pl), the swapped
    German intake sensors 762/763, and the appliance type in 757.
  - French has no source and falls back to English.
Heat pump types (calc[78]): Bouni/python-luxtronik, luxtronik/datatypes.py, HeatpumpCode.

BenPru/luxtronik and Bouni/python-luxtronik are both MIT licensed:
  Copyright (c) 2021 BenPru
  Copyright (c) 2018 Bouni
Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from typing import Dict

from translations import Language

# code -> {language: message}; French is resolved to English by fault_message().
FAULT_MESSAGES: Dict[int, Dict[Language, str]] = {
    701: {
        Language.ENGLISH: "Error low pressure",
        Language.DUTCH: "Lage-drukstoring vergrendeling",
        Language.GERMAN: "Niederdruckstörung",
        Language.POLISH: "Błąd niskiego ciśnienia",
    },
    702: {
        Language.ENGLISH: "Low pressure stop",
        Language.DUTCH: "Lage-drukstoring onderbroken",
        Language.GERMAN: "Niederdrucksperre - RESET automatisch",
        Language.POLISH: "Zatrzymanie przy niskim ciśnieniu",
    },
    703: {
        Language.ENGLISH: "Antifreeze",
        Language.DUTCH: "Vorstbeveiliging",
        Language.GERMAN: "Frostschutz",
        Language.POLISH: "środek przeciw zamarzaniu",
    },
    704: {
        Language.ENGLISH: "Error hot gas",
        Language.DUTCH: "Persgasstoring",
        Language.GERMAN: "Heissgasstörung - Reset automatisch nach Zeitsperre",
        Language.POLISH: "Błąd gorącego gazu",
    },
    705: {
        Language.ENGLISH: "Motor protection VEN",
        Language.DUTCH: "Motorbeveiliging VEN",
        Language.GERMAN: "Motorschutz Ventilator",
        Language.POLISH: "Zabezpieczenie silnika VEN",
    },
    706: {
        Language.ENGLISH: "Motor protection BCP",
        Language.DUTCH: "Motorbeveilig. BSUP",
        Language.GERMAN: "Motorschutz Sole- oder Brunnenwasserumwälzpumpe",
        Language.POLISH: "Zabezpieczenie silnika BCP",
    },
    707: {
        Language.ENGLISH: "Coding of HP",
        Language.DUTCH: "Codering WP",
        Language.GERMAN: "Codierung Wärmepumpe",
        Language.POLISH: "Kodowanie HP",
    },
    708: {
        Language.ENGLISH: "Return sensor",
        Language.DUTCH: "Voeler retourleiding",
        Language.GERMAN: "Fühler Rücklauf",
        Language.POLISH: "Czujnik powrotu",
    },
    709: {
        Language.ENGLISH: "Flow sensor",
        Language.DUTCH: "Voeler aanvoer",
        Language.GERMAN: "Fühler Vorlauf",
        Language.POLISH: "Czujnik przepływu",
    },
    710: {
        Language.ENGLISH: "Hot gas sensor",
        Language.DUTCH: "Temp.voeler persgas",
        Language.GERMAN: "Fühler Heissgas",
        Language.POLISH: "Czujnik gorącego gazu",
    },
    711: {
        Language.ENGLISH: "External temp. sensor",
        Language.DUTCH: "Voeler buitentemp.",
        Language.GERMAN: "Fühler Aussentemp",
        Language.POLISH: "Temperatura zewnętrzna czujnik",
    },
    712: {
        Language.ENGLISH: "Domestic hot water sensor",
        Language.DUTCH: "Voeler tapwater",
        Language.GERMAN: "Fühler Warmwasser",
        Language.POLISH: "Czujnik ciepłej wody użytkowej",
    },
    713: {
        Language.ENGLISH: "HS-on sensor",
        Language.DUTCH: "Voeler WQ-Ein",
        Language.GERMAN: "Fühler Wärmequelle-Ein",
        Language.POLISH: "Czujnik HS-on",
    },
    714: {
        Language.ENGLISH: "Hot gas DHW",
        Language.DUTCH: "Persgas BW",
        Language.GERMAN: "Heissgas Brauchwasser - Reset automatisch nach Zeitsperre",
        Language.POLISH: "Gorący gaz SW",
    },
    715: {
        Language.ENGLISH: "High-pressure switch-off",
        Language.DUTCH: "Hogedrukstoring onderbroken",
        Language.GERMAN: "Hochdruck-Abschaltung - RESET automatisch",
        Language.POLISH: "Wyłączenie wysokiego ciśnienia",
    },
    716: {
        Language.ENGLISH: "High-pressure fault",
        Language.DUTCH: "Hogedrukstoring",
        Language.GERMAN: "Hochdruckstörung - Bitte Inst rufen",
        Language.POLISH: "Usterka wysokiego ciśnienia",
    },
    717: {
        Language.ENGLISH: "Flow rate HS",
        Language.DUTCH: "Doorstroming-WQ",
        Language.GERMAN: "Durchfluss-Wärmequelle",
        Language.POLISH: "Przepływ HS",
    },
    718: {
        Language.ENGLISH: "Max. outside temp",
        Language.DUTCH: "Max. buitentemp.",
        Language.GERMAN: "Max. Aussentemperatur - RESET automatisch",
        Language.POLISH: "Maks. temp. zew",
    },
    719: {
        Language.ENGLISH: "Min. outside temp",
        Language.DUTCH: "Min. buitentemp.",
        Language.GERMAN: "Min. Aussentemperatur - RESET automatisch",
        Language.POLISH: "Min. temp. zew",
    },
    720: {
        Language.ENGLISH: "HS temperature",
        Language.DUTCH: "WQ-temperatuur",
        Language.GERMAN: "Wärmequelle-Temperatur - RESET automatisch nach Zeitsperre",
        Language.POLISH: "Temperatura HS",
    },
    721: {
        Language.ENGLISH: "Low-pressure switch-off",
        Language.DUTCH: "Lagedrukuitschakeling",
        Language.GERMAN: "Niederdruckabschaltung - RESET automatisch",
        Language.POLISH: "Wyłączenie przy niskim ciśnieniu",
    },
    722: {
        Language.ENGLISH: "Tempdiff HW",
        Language.DUTCH: "Tempdiff VW",
        Language.GERMAN: "Tempdiff Heizwasser",
        Language.POLISH: "Tempdiff HW",
    },
    723: {
        Language.ENGLISH: "Tempdiff DHW",
        Language.DUTCH: "Tempdiff tapw.",
        Language.GERMAN: "Tempdiff Warmwasser",
        Language.POLISH: "Tempdiff SW",
    },
    724: {
        Language.ENGLISH: "Tempdiff defrosting",
        Language.DUTCH: "Tempdiff ABT",
        Language.GERMAN: "Tempdiff Abtauen",
        Language.POLISH: "Rozmrażanie Tempdiff",
    },
    725: {
        Language.ENGLISH: "System error DHW",
        Language.DUTCH: "Installatiefout TW",
        Language.GERMAN: "Anlagefehler Brauchwasser",
        Language.POLISH: "Błąd systemowy SW",
    },
    726: {
        Language.ENGLISH: "Sensor mixing circ 1",
        Language.DUTCH: "Voeler mengcircuit 1",
        Language.GERMAN: "Fühler Mischkreis 1",
        Language.POLISH: "Czujnik obiegu mieszania 1",
    },
    727: {
        Language.ENGLISH: "Brine pressure",
        Language.DUTCH: "Druk brinecircuit",
        Language.GERMAN: "Soledruck",
        Language.POLISH: "Ciśnienie solanki",
    },
    728: {
        Language.ENGLISH: "Sensor HS Off",
        Language.DUTCH: "Voeler WQ-Uit",
        Language.GERMAN: "Fühler Wärmequelle-Aus",
        Language.POLISH: "Czujnik HS wyłączony",
    },
    729: {
        Language.ENGLISH: "Rotating field error",
        Language.DUTCH: "Draaiveld storing",
        Language.GERMAN: "Drehfeldfehler",
        Language.POLISH: "Błąd pola wirującego",
    },
    730: {
        Language.ENGLISH: "Screed heating error",
        Language.DUTCH: "Vermogenstekort OWP",
        Language.GERMAN: "Leistung Ausheizen",
        Language.POLISH: "Błąd programu wygrzewania jastrychu",
    },
    731: {
        Language.ENGLISH: "Timeout TDI",
        Language.DUTCH: "Time-out TDI",
        Language.GERMAN: "Zeitüberschreitung TDI",
        Language.POLISH: "Przekroczenie czasu TDI",
    },
    732: {
        Language.ENGLISH: "Cooling fault",
        Language.DUTCH: "Storing koeling",
        Language.GERMAN: "Störung Kühlung",
        Language.POLISH: "Usterka chłodzenia",
    },
    733: {
        Language.ENGLISH: "Anode fault",
        Language.DUTCH: "Storing anode",
        Language.GERMAN: "Störung Anode",
        Language.POLISH: "Usterka anody",
    },
    734: {
        Language.ENGLISH: "Anode fault",
        Language.DUTCH: "Storing anode",
        Language.GERMAN: "Störung Anode",
        Language.POLISH: "Usterka anody",
    },
    735: {
        Language.ENGLISH: "Error Ext. En",
        Language.DUTCH: "Ext. En",
        Language.GERMAN: "Fühler Externe Energiequelle",
        Language.POLISH: "Błąd zew. Pl",
    },
    736: {
        Language.ENGLISH: "Error solar collector",
        Language.DUTCH: "Sensor zonnecollector",
        Language.GERMAN: "Fühler Solarkollektor",
        Language.POLISH: "Błąd kolektora słonecznego",
    },
    737: {
        Language.ENGLISH: "Error solar tank",
        Language.DUTCH: "Voeler buffervat zonnecollector",
        Language.GERMAN: "Fühler Solarspeicher",
        Language.POLISH: "Błąd zasobnika solarnego",
    },
    738: {
        Language.ENGLISH: "Error mixing circle 2",
        Language.DUTCH: "Voeler menggroep2",
        Language.GERMAN: "Fühler Mischkreis2",
        Language.POLISH: "Błąd mieszania koła 2",
    },
    739: {
        Language.ENGLISH: "Error mixing circle 3",
        Language.DUTCH: "Voeler menggroep3",
        Language.GERMAN: "Fühler Mischkreis 3",
        Language.POLISH: "Czujnik obwodu mieszającego 3",
    },
    750: {
        Language.ENGLISH: "Return sensor external",
        Language.DUTCH: "Voeler retourleiding",
        Language.GERMAN: "Fühler Rücklauf extern",
        Language.POLISH: "Czujnik powrotu zewnętrzny",
    },
    751: {
        Language.ENGLISH: "Phase monitoring fault",
        Language.DUTCH: "Fasebewakingsfout",
        Language.GERMAN: "Phasenüberwachungsfehler",
        Language.POLISH: "Błąd monitorowania fazy",
    },
    752: {
        Language.ENGLISH: "Flow error",
        Language.DUTCH: "Doorstromingsfout",
        Language.GERMAN: "Phasenüberwachungs / Durchflussfehler",
        Language.POLISH: "Błąd przepływu",
    },
    755: {
        Language.ENGLISH: "Lost connection to slave",
        Language.DUTCH: "Verbinding met slave verloren",
        Language.GERMAN: "Verbindung zu Slave verloren",
        Language.POLISH: "Utracono połączenie z modułem slave",
    },
    756: {
        Language.ENGLISH: "Lost connection to master",
        Language.DUTCH: "Verbinding met master verloren",
        Language.GERMAN: "Verbindung zu Master verloren",
        Language.POLISH: "Utracono połączenie z masterem",
    },
    757: {
        Language.ENGLISH: "Low-pressure fault in DHW heat pump",
        Language.DUTCH: "LD-storing bij WW-apparaat",
        Language.GERMAN: "Niederdruck-Störung bei Brauchwasser-Gerät",
        Language.POLISH: "Usterka niskiego ciśnienia w urządzeniu CWU",
    },
    758: {
        Language.ENGLISH: "Defrosting malfunction",
        Language.DUTCH: "Storing ontdooiing",
        Language.GERMAN: "Störung Abtauung",
        Language.POLISH: "Usterka rozmrażania",
    },
    759: {
        Language.ENGLISH: "TDI message",
        Language.DUTCH: "Melding TDI",
        Language.GERMAN: "Meldung thermische Desinfektion",
        Language.POLISH: "Komunikat TDI",
    },
    760: {
        Language.ENGLISH: "Defrosting fault",
        Language.DUTCH: "Storing ontdooiing",
        Language.GERMAN: "Störung Abtauung",
        Language.POLISH: "Błąd rozmrażania",
    },
    761: {
        Language.ENGLISH: "LIN timeout/LIN-connection lost",
        Language.DUTCH: "LIN-timeout",
        Language.GERMAN: "LIN-Verbindung unterbrochen",
        Language.POLISH: "Przekroczenie limitu czasu LIN/utracono połączenie LIN",
    },
    762: {
        Language.ENGLISH: "sensor (evaporator intake)",
        Language.DUTCH: "Voeler (aanzuiging verdamper)",
        Language.GERMAN: "Fühler Ansaug-Verdampfer",
        Language.POLISH: "czujnik (wlot parownika)",
    },
    763: {
        Language.ENGLISH: "sensor (compressor intake)",
        Language.DUTCH: "Voeler (aanzuiging compressor)",
        Language.GERMAN: "Fühler Ansaug-Verdichter",
        Language.POLISH: "czujnik (wlot sprężarki)",
    },
    764: {
        Language.ENGLISH: "Sensor Compressor heater",
        Language.DUTCH: "Voeler Compressorverwarming",
        Language.GERMAN: "Fühler Verdichterheizung",
        Language.POLISH: "Czujnik Grzałka sprężarki",
    },
    765: {
        Language.ENGLISH: "Overheating",
        Language.DUTCH: "Oververhitting",
        Language.GERMAN: "überhitzung",
        Language.POLISH: "Przegrzanie",
    },
    766: {
        Language.ENGLISH: "compressor's functional range",
        Language.DUTCH: "Toepassingsgebied compressor",
        Language.GERMAN: "Einsatzgrenzen-Verdichter",
        Language.POLISH: "zakres funkcjonalny sprężarki",
    },
    767: {
        Language.ENGLISH: "STB E-Rod",
        Language.DUTCH: "STB E-element",
        Language.GERMAN: "Sicherheitstemperaturbegrenzer Heizstab",
        Language.POLISH: "STB E-Rod",
    },
    768: {
        Language.ENGLISH: "Flow monitoring",
        Language.DUTCH: "Doorstromingsbewaking",
        Language.GERMAN: "Durchflussüberwachung",
        Language.POLISH: "Monitorowanie przepływu",
    },
    769: {
        Language.ENGLISH: "Pump control",
        Language.DUTCH: "Pompaansturing",
        Language.GERMAN: "Pumpenansteuerung",
        Language.POLISH: "Sterowanie pompą",
    },
    770: {
        Language.ENGLISH: "Low superheat",
        Language.DUTCH: "Lage oververhitting",
        Language.GERMAN: "Niedrige überhitzung",
        Language.POLISH: "Niskie przegrzanie",
    },
    771: {
        Language.ENGLISH: "High superheat",
        Language.DUTCH: "Hoge oververhitting",
        Language.GERMAN: "Hohe überhitzung",
        Language.POLISH: "Wysokie przegrzanie",
    },
    776: {
        Language.ENGLISH: "limit of application-CP",
        Language.DUTCH: "Toepassingsgebied compressor",
        Language.GERMAN: "Einsatzgrenzen-Verdichter",
        Language.POLISH: "granica zastosowania-CP",
    },
    777: {
        Language.ENGLISH: "Expansion valve",
        Language.DUTCH: "Expansieventiel",
        Language.GERMAN: "Expansionsventil",
        Language.POLISH: "Zawór rozprężny",
    },
    778: {
        Language.ENGLISH: "Low pressure sensor",
        Language.DUTCH: "Lage druk voeler",
        Language.GERMAN: "Fühler Niederdruck",
        Language.POLISH: "Czujnik niskiego ciśnienia",
    },
    779: {
        Language.ENGLISH: "High pressure sensor",
        Language.DUTCH: "Hoge druk voeler",
        Language.GERMAN: "Fühler Hochdruck",
        Language.POLISH: "Czujnik wysokiego ciśnienia",
    },
    780: {
        Language.ENGLISH: "EVI sensor",
        Language.DUTCH: "EVI voeler",
        Language.GERMAN: "Fühler EVI",
        Language.POLISH: "Czujnik EVI",
    },
    781: {
        Language.ENGLISH: "Liquid temp. sensor before EXV",
        Language.DUTCH: "Gasvoeler voor Exp. ventiel",
        Language.GERMAN: "Fühler Flüssig, vor Ex-Ventil",
        Language.POLISH: "Temperatura cieczy czujnik przed EXV",
    },
    782: {
        Language.ENGLISH: "Suction gas EVI temp. sensor",
        Language.DUTCH: "EVI zuiggas voeler",
        Language.GERMAN: "Fühler EVI (Enhanced Vapour Injection) Sauggas",
        Language.POLISH: "Temp. gazu zasysanego EVI czujnik",
    },
    783: {
        Language.ENGLISH: "Communication SEC - Inverter",
        Language.DUTCH: "Comunicatie SEC - Inverter",
        Language.GERMAN: "Kommunikation SEC-Inverter",
        Language.POLISH: "Komunikacja SEC – Falownik",
    },
    784: {
        Language.ENGLISH: "VSS lockdown",
        Language.DUTCH: "VSS geblokkeerd 2 min onderbr.",
        Language.GERMAN: "VSS gesperrt",
        Language.POLISH: "Blokada VSS",
    },
    785: {
        Language.ENGLISH: "SEC-Board defective",
        Language.DUTCH: "SEC-Board defect",
        Language.GERMAN: "SEC-Board defekt",
        Language.POLISH: "Uszkodzona płyta SEC",
    },
    786: {
        Language.ENGLISH: "Communication SEC - HZ/IO",
        Language.DUTCH: "Comunicatie SEC - Inverter",
        Language.GERMAN: "Kommunikation SEC-Inverter",
        Language.POLISH: "Komunikacja SEC - HZ/IO",
    },
    787: {
        Language.ENGLISH: "VD alert",
        Language.DUTCH: "Compr. alarm",
        Language.GERMAN: "VD Alarm",
        Language.POLISH: "Alarm VD",
    },
    788: {
        Language.ENGLISH: "Severe inverter fault",
        Language.DUTCH: "Ernstige inverter fout",
        Language.GERMAN: "Schwerw. Inverter Fehler",
        Language.POLISH: "Poważna usterka falownika",
    },
    789: {
        Language.ENGLISH: "LIN/Encoding not found",
        Language.DUTCH: "LIN/codering niet beschikbaar",
        Language.GERMAN: "LIN/Kodierung nicht vorhanden",
        Language.POLISH: "Nie znaleziono LIN/kodowania",
    },
    790: {
        Language.ENGLISH: "Severe inverter fault",
        Language.DUTCH: "Ernstige inverter fout",
        Language.GERMAN: "Schwerw. Inverter Fehler",
        Language.POLISH: "Poważna usterka falownika",
    },
    791: {
        Language.ENGLISH: "Lost ModBus communication",
        Language.DUTCH: "ModBus verbinding verloren",
        Language.GERMAN: "ModBus Verbindung verloren",
        Language.POLISH: "Utracono komunikację ModBus",
    },
    792: {
        Language.ENGLISH: "LIN-connection lost",
        Language.DUTCH: "LIN-verbinding verbroken",
        Language.GERMAN: "LIN-Verbindung unterbrochen",
        Language.POLISH: "Utracono połączenie LIN",
    },
    793: {
        Language.ENGLISH: "Severe inverter fault",
        Language.DUTCH: "Ernstige inverter fout",
        Language.GERMAN: "Schwerw. Inverter Fehler",
        Language.POLISH: "Poważna usterka falownika",
    },
    794: {
        Language.ENGLISH: "Overvoltage",
        Language.DUTCH: "Overspanning",
        Language.GERMAN: "Überspannung",
        Language.POLISH: "Przepięcie",
    },
    795: {
        Language.ENGLISH: "Undervoltage",
        Language.DUTCH: "Onderspanning",
        Language.GERMAN: "Unterspannung",
        Language.POLISH: "Zbyt niskie napięcie",
    },
    796: {
        Language.ENGLISH: "Safety switch off",
        Language.DUTCH: "Veiligheidsuitschakeling",
        Language.GERMAN: "Sicherheitsabschaltung",
        Language.POLISH: "Wyłączenie bezpieczeństwa",
    },
    797: {
        Language.ENGLISH: "MLRH is not supported",
        Language.DUTCH: "MLRH wordt niet ondersteund",
        Language.GERMAN: "MLRH wird nicht unterstützt",
        Language.POLISH: "MLRH nie jest obsługiwane",
    },
    798: {
        Language.ENGLISH: "ModBus Fan",
        Language.DUTCH: "ModBus-verbinding verloren",
        Language.GERMAN: "ModBus Ventilator",
        Language.POLISH: "ModBus wentylator",
    },
    799: {
        Language.ENGLISH: "ModBus ASB",
        Language.DUTCH: "ModBus-verbinding verloren",
        Language.GERMAN: "ModBus ASB",
        Language.POLISH: "ModBus ASB",
    },
    800: {
        Language.ENGLISH: "Desuperheater-error",
        Language.DUTCH: "Desuperheater-fout",
        Language.GERMAN: "Enthitzer-Fehler",
        Language.POLISH: "Błąd desuperheatera",
    },
    802: {
        Language.ENGLISH: "Switchbox fan",
        Language.DUTCH: "Switchbox fan",
        Language.GERMAN: "Ventilator Schaltkasten",
        Language.POLISH: "Wentylator skrzynki rozdzielczej",
    },
    803: {
        Language.ENGLISH: "Switchbox fan",
        Language.DUTCH: "Switchbox fan",
        Language.GERMAN: "Ventilator Schaltkasten",
        Language.POLISH: "Wentylator skrzynki rozdzielczej",
    },
    806: {
        Language.ENGLISH: "ModBus SEC",
        Language.DUTCH: "ModBus SEC",
        Language.GERMAN: "ModBus SEC",
        Language.POLISH: "ModBus SEC",
    },
    807: {
        Language.ENGLISH: "Lost ModBus connection",
        Language.DUTCH: "ModBus-verbinding verloren",
        Language.GERMAN: "ModBus Verbindung verloren",
        Language.POLISH: "Utracone połączenie ModBus",
    },
}

# calc[78] heat pump type code -> model designation
HEATPUMP_TYPES: Dict[int, str] = {
    0: "ERC",
    1: "SW1",
    2: "SW2",
    3: "WW1",
    4: "WW2",
    5: "L1I",
    6: "L2I",
    7: "L1A",
    8: "L2A",
    9: "KSW",
    10: "KLW",
    11: "SWC",
    12: "LWC",
    13: "L2G",
    14: "WZS",
    15: "L1I407",
    16: "L2I407",
    17: "L1A407",
    18: "L2A407",
    19: "L2G407",
    20: "LWC407",
    21: "L1AREV",
    22: "L2AREV",
    23: "WWC1",
    24: "WWC2",
    25: "L2G404",
    26: "WZW",
    27: "L1S",
    28: "L1H",
    29: "L2H",
    30: "WZWD",
    31: "ERC",
    32: "ERC",
    33: "ERC",
    34: "ERC",
    35: "ERC",
    36: "ERC",
    37: "ERC",
    38: "ERC",
    39: "ERC",
    40: "WWB_20",
    41: "LD5",
    42: "LD7",
    43: "SW 37_45",
    44: "SW 58_69",
    45: "SW 29_56",
    46: "LD5 (230V)",
    47: "LD7 (230 V)",
    48: "LD9",
    49: "LD5 REV",
    50: "LD7 REV",
    51: "LD5 REV 230V",
    52: "LD7 REV 230V",
    53: "LD9 REV 230V",
    54: "SW 291",
    55: "LW SEC",
    56: "HMD 2",
    57: "MSW 4",
    58: "MSW 6",
    59: "MSW 8",
    60: "MSW 10",
    61: "MSW 12",
    62: "MSW 14",
    63: "MSW 17",
    64: "MSW 19",
    65: "MSW 23",
    66: "MSW 26",
    67: "MSW 30",
    68: "MSW 4S",
    69: "MSW 6S",
    70: "MSW 8S",
    71: "MSW 10S",
    72: "MSW 12S",
    73: "MSW 16S",
    74: "MSW2-6S",
    75: "MSW4-16",
    76: "LD2AG",
    77: "LD9V",
    78: "MSW3-12",
    79: "MSW3-12S",
    80: "MSW2-9S",
    81: "LW 8",
    82: "LW 12",
    83: "HZ_HMD",
    84: "LW V4",
    85: "LW SEC 2",
    86: "MSW1-4S",
    87: "LP5V",
    88: "LP8V",
}


def fault_message(code: int, language: Language) -> str | None:
    """The message for a fault code in the given language, or None for an unknown code."""
    messages = FAULT_MESSAGES.get(code)
    if messages is None:
        return None
    return messages.get(language) or messages[Language.ENGLISH]


def heatpump_type(code: int) -> str | None:
    """The model designation for a calc[78] type code, or None for an unknown code."""
    return HEATPUMP_TYPES.get(code)
