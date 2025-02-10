from enum import Enum, auto

class Language(Enum):
    """Supported languages"""
    ENGLISH = auto()
    POLISH = auto()
    DUTCH = auto()
    GERMAN = auto()
    FRENCH = auto()


# Define translations
TRANSLATIONS = {
    # Device names (max ~20 characters)
    'Heat supply temp': {
        Language.ENGLISH: 'Heat supply temp',
        Language.POLISH: 'Temp zasilania',
        Language.DUTCH: 'Aanvoertemp',
        Language.GERMAN: 'Vorlauftemp.',
        Language.FRENCH: "Temp. alim."
    },
    'Heat return temp': {
        Language.ENGLISH: 'Heat return temp',
        Language.POLISH: 'Temp powrotu',
        Language.DUTCH: 'Retourtemp',
        Language.GERMAN: 'Rücklauftemp.',
        Language.FRENCH: 'Temp. retour'
    },
    'Return temp target': {
        Language.ENGLISH: 'Return temp target',
        Language.POLISH: 'Temp powr cel',
        Language.DUTCH: 'Retour doel',
        Language.GERMAN: 'Soll-Rückl.t',
        Language.FRENCH: 'Temp. ret. cib.'
    },
    'Outside temp': {
        Language.ENGLISH: 'Outside temp',
        Language.POLISH: 'Temp zewnętrzna',
        Language.DUTCH: 'Buitentemp',
        Language.GERMAN: 'Außentemp.',
        Language.FRENCH: 'Temp. ext.'
    },
    'Outside temp avg': {
        Language.ENGLISH: 'Outside temp avg',
        Language.POLISH: 'Temp zewn. śred',
        Language.DUTCH: 'Buitent. gem',
        Language.GERMAN: 'Ø Außentemp.',
        Language.FRENCH: 'Moy. temp.ext.'
    },
    'DHW temp': {
        Language.ENGLISH: 'DHW temp',
        Language.POLISH: 'Temp CWU',
        Language.DUTCH: 'Tapw. temp',
        Language.GERMAN: 'Warmw. temp.',
        Language.FRENCH: "Temp. eau CS"
    },
    'DHW temp target': {
        Language.ENGLISH: 'DHW temp target',
        Language.POLISH: 'Temp CWU cel',
        Language.DUTCH: 'Tapw. inst',
        Language.GERMAN: 'Soll Warmw.temp',
        Language.FRENCH: "Temp. eau CS cib"
    },
    'WP source in temp': {
        Language.ENGLISH: 'WP source in temp',
        Language.POLISH: 'Temp WP źródł. wej',
        Language.DUTCH: 'WP in temp',
        Language.GERMAN: 'Quellentemp. ein',
        Language.FRENCH: 'Temp. entr. source'
    },
    'WP source out temp': {
        Language.ENGLISH: 'WP source out temp',
        Language.POLISH: 'Temp WP źródł. wyj',
        Language.DUTCH: 'WP uit temp',
        Language.GERMAN: 'Quellentemp. aus',
        Language.FRENCH: 'Temp. sor. source'
    },
    'MC1 temp': {
        Language.ENGLISH: 'MC1 temp',
        Language.POLISH: 'Temp OM1',
        Language.DUTCH: 'Temp MG1',
        Language.GERMAN: 'Mischkreis 1',
        Language.FRENCH: 'Temp. circ. 1'
    },
    'MC1 temp target': {
        Language.ENGLISH: 'MC1 temp target',
        Language.POLISH: 'Temp OM1 cel',
        Language.DUTCH: 'Inst MG1',
        Language.GERMAN: 'Soll MG 1',
        Language.FRENCH: 'Circ. 1 cible'
    },
    'MC2 temp': {
        Language.ENGLISH: 'MC2 temp',
        Language.POLISH: 'Temp OM2',
        Language.DUTCH: 'Temp MG2',
        Language.GERMAN: 'Mischkreis 2',
        Language.FRENCH: 'Temp. circ. 2'
    },
    'MC2 temp target': {
        Language.ENGLISH: 'MC2 temp target',
        Language.POLISH: 'Temp OM2 cel',
        Language.DUTCH: 'Inst MG2',
        Language.GERMAN: 'Soll MG 2',
        Language.FRENCH: 'Circ. 2 cible'
    },
    'Heating mode': {
        Language.ENGLISH: 'Heating mode',
        Language.POLISH: 'Obieg grzewczy',
        Language.DUTCH: 'Verwarmen',
        Language.GERMAN: 'Heizmodus',
        Language.FRENCH: 'Mode chauf.'
    },
    'Hot water mode': {
        Language.ENGLISH: 'Hot water mode',
        Language.POLISH: 'Woda użytkowa',
        Language.DUTCH: 'Warmwater',
        Language.GERMAN: 'Warmw.-modus',
        Language.FRENCH: 'Mode ECS'
    },
    'Cooling': {
        Language.ENGLISH: 'Cooling',
        Language.POLISH: 'Chłodzenie',
        Language.DUTCH: 'Koeling',
        Language.GERMAN: 'Kühlung',
        Language.FRENCH: 'Refroid.'
    },
    'Automatic': {
        Language.ENGLISH: 'Automatic',
        Language.POLISH: 'Automatyczny',
        Language.DUTCH: 'Automatisch',
        Language.GERMAN: 'Automatisch',
        Language.FRENCH: 'Auto'
    },
    '2nd heat source': {
        Language.ENGLISH: '2nd heat source',
        Language.POLISH: 'II źr. ciepła',
        Language.DUTCH: '2e warm.opwek',
        Language.GERMAN: '2. Wärmequ.',
        Language.FRENCH: '2e source chauf.'
    },
    'Party': {
        Language.ENGLISH: 'Party',
        Language.POLISH: 'Party',
        Language.DUTCH: 'Party',
        Language.GERMAN: 'Party',
        Language.FRENCH: 'Fête'
    },
    'Holidays': {
        Language.ENGLISH: 'Holidays',
        Language.POLISH: 'Wakacje',
        Language.DUTCH: 'Vakantie',
        Language.GERMAN: 'Urlaub',
        Language.FRENCH: 'Vacances'
    },
    'Off': {
        Language.ENGLISH: 'Off',
        Language.POLISH: 'Wył.',
        Language.DUTCH: 'Uit',
        Language.GERMAN: 'Aus',
        Language.FRENCH: 'Arrêt'
    },
    'No requirement': {
        Language.ENGLISH: 'No requirement',
        Language.POLISH: 'Brak zapotrzeb.',
        Language.DUTCH: 'Geen warmtevraag',
        Language.GERMAN: 'Kein Bedarf',
        Language.FRENCH: 'Aucune dem.'
    },
    'Swimming pool mode / Photovoltaik': {
        Language.ENGLISH: 'Pool/Photovoltaik',
        Language.POLISH: 'Basen/Fotowoltaika',
        Language.DUTCH: 'Zwembad/Fotovolt',
        Language.GERMAN: 'Pool/Photovoltaik',
        Language.FRENCH: 'Piscine/Photovolt'
    },
    'EVUM': {
        Language.ENGLISH: 'EVUM',
        Language.POLISH: 'EVU',
        Language.DUTCH: 'EVU',
        Language.GERMAN: 'EVUM',
        Language.FRENCH: 'EVUM'
    },
    'Defrost': {
        Language.ENGLISH: 'Defrost',
        Language.POLISH: 'Rozmrażanie',
        Language.DUTCH: 'Ontdooien',
        Language.GERMAN: 'Abtauung',
        Language.FRENCH: 'Dégivrage'
    },
    'Heating external source mode': {
        Language.ENGLISH: 'Ext. heat mode',
        Language.POLISH: 'Ogrzewanie zewn.',
        Language.DUTCH: 'Externe verw.',
        Language.GERMAN: 'Externer Modus',
        Language.FRENCH: 'Mode chauf. ext.'
    },
    'Temp +-': {
        Language.ENGLISH: 'Temp +-',
        Language.POLISH: 'Temp +-',
        Language.DUTCH: 'Temp +-',
        Language.GERMAN: 'Temp +-',
        Language.FRENCH: 'Temp +-'
    },
    'Working mode': {
        Language.ENGLISH: 'Working mode',
        Language.POLISH: 'Stan pracy',
        Language.DUTCH: 'Bedrijfsmode',
        Language.GERMAN: 'Betriebsmodus',
        Language.FRENCH: 'Mode travail'
    },
    'Flow': {
        Language.ENGLISH: 'Flow',
        Language.POLISH: 'Przepływ',
        Language.DUTCH: 'Debiet',
        Language.GERMAN: 'Durchfluss',
        Language.FRENCH: 'Débit'
    },
    'Compressor freq': {
        Language.ENGLISH: 'Compressor freq',
        Language.POLISH: 'Częst sprężarki',
        Language.DUTCH: 'Compr freq',
        Language.GERMAN: 'Kompressorfrq.',
        Language.FRENCH: 'Fréq. comp.'
    },
    'Room temp': {
        Language.ENGLISH: 'Room temp',
        Language.POLISH: 'Temp pokojowa',
        Language.DUTCH: 'Ruimtetemp',
        Language.GERMAN: 'Raumtemp.',
        Language.FRENCH: 'Temp. amb.'
    },
    'Room temp target': {
        Language.ENGLISH: 'Room temp target',
        Language.POLISH: 'Temp pokoj cel',
        Language.DUTCH: 'Ruimtet. doel',
        Language.GERMAN: 'Soll-Raumtemp.',
        Language.FRENCH: 'Temp. amb. cib.'
    },
    'Power total': {
        Language.ENGLISH: 'Power total',
        Language.POLISH: 'Pobór mocy',
        Language.DUTCH: 'Energie totaal',
        Language.GERMAN: 'Gesamtleistung',
        Language.FRENCH: 'Puiss. totale'
    },
    'Power heating': {
        Language.ENGLISH: 'Power heating',
        Language.POLISH: 'Pobór grz',
        Language.DUTCH: 'Energie verw',
        Language.GERMAN: 'Heizleistung',
        Language.FRENCH: 'Puiss. chauf.'
    },
    'Power DHW': {
        Language.ENGLISH: 'Power DHW',
        Language.POLISH: 'Pobór CWU',
        Language.DUTCH: 'Energie tapw',
        Language.GERMAN: 'Warmwasserleis.',
        Language.FRENCH: "Puiss. ECS"
    },
    'Heat out total': {
        Language.ENGLISH: 'Heat out total',
        Language.POLISH: 'Moc grz razem',
        Language.DUTCH: 'Verwarm totaal',
        Language.GERMAN: 'Gesamtwärmeabg.',
        Language.FRENCH: 'Chaleur tot.'
    },
    'Heat out heating': {
        Language.ENGLISH: 'Heat out heating',
        Language.POLISH: 'Moc grz ogrz',
        Language.DUTCH: 'Verwarm verw',
        Language.GERMAN: 'Heizwärmeabg.',
        Language.FRENCH: 'Chaleur chauf.'
    },
    'Heat out DHW': {
        Language.ENGLISH: 'Heat out DHW',
        Language.POLISH: 'Moc grz CWU',
        Language.DUTCH: 'Verwarm tapw',
        Language.GERMAN: 'Wärmeabg. ECS',
        Language.FRENCH: 'Chaleur ECS'
    },
    'COP total': {
        Language.ENGLISH: 'COP total',
        Language.POLISH: 'COP razem',
        Language.DUTCH: 'COP totaal',
        Language.GERMAN: 'Gesamt-COP',
        Language.FRENCH: 'COP total'
    },
    'Heating pump speed': {
        Language.ENGLISH: 'Heating pump speed',
        Language.POLISH: 'Pompa CO proc.',
        Language.DUTCH: 'CV pomp snelheid',
        Language.GERMAN: 'Heizp. Geschw.',
        Language.FRENCH: 'Vit. pompe chauf.'
    },
    'Brine pump speed': {
        Language.ENGLISH: 'Brine pump speed',
        Language.POLISH: 'Pompa DZ proc.',
        Language.DUTCH: 'Bronpomp snelheid',
        Language.GERMAN: 'Solep. Geschw.',
        Language.FRENCH: 'Vit. pompe sole'
    },
    'Hot gas temp': {
        Language.ENGLISH: 'Hot gas temp',
        Language.POLISH: 'Temp gazu gorącego',
        Language.DUTCH: 'Heetgas temp',
        Language.GERMAN: 'Heißgastemp.',
        Language.FRENCH: 'Temp. gaz chaud'
    },
    'Suction temp': {
        Language.ENGLISH: 'Suction temp',
        Language.POLISH: 'Temp zasysania',
        Language.DUTCH: 'Aanzuig temp',
        Language.GERMAN: 'Saugtemp.',
        Language.FRENCH: "Temp. d'aspir."
    },
    'Superheat': {
        Language.ENGLISH: 'Superheat',
        Language.POLISH: 'Przegrzanie',
        Language.DUTCH: 'Oververhitting',
        Language.GERMAN: 'Überhitzung',
        Language.FRENCH: 'Surchauffe'
    },
    'High pressure': {
        Language.ENGLISH: 'High pressure',
        Language.POLISH: 'Wysokie ciśnienie',
        Language.DUTCH: 'Hoge druk',
        Language.GERMAN: 'Hochdruck',
        Language.FRENCH: 'Haute pression'
    },
    'Low pressure': {
        Language.ENGLISH: 'Low pressure',
        Language.POLISH: 'Niskie ciśnienie',
        Language.DUTCH: 'Lage druk',
        Language.GERMAN: 'Niederdruck',
        Language.FRENCH: 'Basse pression'
    },
    'Brine temp diff': {
        Language.ENGLISH: 'Brine temp diff',
        Language.POLISH: 'Różnica temp DZ',
        Language.DUTCH: 'Bron temp vers.',
        Language.GERMAN: 'Soletemp.-diff.',
        Language.FRENCH: 'Diff. temp. sole'
    },
    'Heating temp diff': {
        Language.ENGLISH: 'Heating temp diff',
        Language.POLISH: 'Różnica temp CO',
        Language.DUTCH: 'CV temp vers.',
        Language.GERMAN: 'Heiztemp.-diff.',
        Language.FRENCH: 'Diff. temp. chauf.'
    },

    # Ranges (detailed descriptions, no length limit)
    'ranges': {
        'superheat': {
            Language.ENGLISH: {
                'description': 'Optimal range: 5-8K\n• <3K: Critical Low (Compressor risk)\n• 3-5K: Low\n• 5-8K: Normal\n• 8-10K: High\n• >10K: Critical High',
            },
            Language.POLISH: {
                'description': 'Zakres optymalny: 5-8K\n• <3K: Krytycznie niski (ryzyko sprężarki)\n• 3-5K: Niski\n• 5-8K: Normalny\n• 8-10K: Wysoki\n• >10K: Krytycznie wysoki',
            },
            Language.DUTCH: {
                'description': 'Optimaal bereik: 5-8K\n• <3K: Kritisch laag (compressor risico)\n• 3-5K: Laag\n• 5-8K: Normaal\n• 8-10K: Hoog\n• >10K: Kritisch hoog',
            },
            Language.GERMAN: {
                'description': 'Optimalbereich: 5-8K\n• <3K: Kritisch niedrig (Kompressorrisiko)\n• 3-5K: Niedrig\n• 5-8K: Normal\n• 8-10K: Hoch\n• >10K: Kritisch hoch',
            },
            Language.FRENCH: {
                'description': 'Plage optimale: 5-8K\n• <3K: Critiquement bas (risque pour le compresseur)\n• 3-5K: Bas\n• 5-8K: Normal\n• 8-10K: Élevé\n• >10K: Critiquement élevé',
            }
        },
        'pressure_high': {
            Language.ENGLISH: {
                'description': 'Optimal range: 16-23 bar\n• <16 bar: Low (Check refrigerant)\n• 16-23 bar: Normal\n• 23-28 bar: High\n• >28 bar: Critical (System shutdown)',
            },
            Language.POLISH: {
                'description': 'Zakres optymalny: 16-23 bar\n• <16 bar: Niskie (Sprawdź czynnik)\n• 16-23 bar: Normalne\n• 23-28 bar: Wysokie\n• >28 bar: Krytyczne (Wyłączenie)',
            },
            Language.DUTCH: {
                'description': 'Optimaal bereik: 16-23 bar\n• <16 bar: Laag (Controleer koudemiddel)\n• 16-23 bar: Normaal\n• 23-28 bar: Hoog\n• >28 bar: Kritisch (Systeem stop)',
            },
            Language.GERMAN: {
                'description': 'Optimalbereich: 16-23 bar\n• <16 bar: Niedrig (Kältemittel prüfen)\n• 16-23 bar: Normal\n• 23-28 bar: Hoch\n• >28 bar: Kritisch (Systemabschaltung)',
            },
            Language.FRENCH: {
                'description': 'Plage optimale: 16-23 bar\n• <16 bar: Faible (vérifier le réfrigérant)\n• 16-23 bar: Normal\n• 23-28 bar: Élevé\n• >28 bar: Critique (arrêt du système)',
            }
        },
        'pressure_low': {
            Language.ENGLISH: {
                'description': 'Optimal range: 4.5-6 bar\n• <3 bar: Critical (Leak check)\n• 3-4.5 bar: Low\n• 4.5-6 bar: Normal\n• >6 bar: High (Check expansion valve)',
            },
            Language.POLISH: {
                'description': 'Zakres optymalny: 4.5-6 bar\n• <3 bar: Krytyczne (Sprawdź szczelność)\n• 3-4.5 bar: Niskie\n• 4.5-6 bar: Normalne\n• >6 bar: Wysokie (Sprawdź zawór)',
            },
            Language.DUTCH: {
                'description': 'Optimaal bereik: 4.5-6 bar\n• <3 bar: Kritisch (Controleer lekkage)\n• 3-4.5 bar: Laag\n• 4.5-6 bar: Normaal\n• >6 bar: Hoog (Controleer expansieventiel)',
            },
            Language.GERMAN: {
                'description': 'Optimalbereich: 4.5-6 bar\n• <3 bar: Kritisch (Lecksuche)\n• 3-4.5 bar: Niedrig\n• 4.5-6 bar: Normal\n• >6 bar: Hoch (Expansionsventil prüfen)',
            },
            Language.FRENCH: {
                'description': 'Plage optimale: 4.5-6 bar\n• <3 bar: Critique (vérifier les fuites)\n• 3-4.5 bar: Faible\n• 4.5-6 bar: Normal\n• >6 bar: Élevé (vérifier la vanne d\'expansion)',
            }
        },
        'hot_gas': {
            Language.ENGLISH: {
                'description': 'Optimal range: <85°C\n• <85°C: Normal\n• 85-95°C: High (Monitor system)\n• >95°C: Critical (Risk of damage)',
            },
            Language.POLISH: {
                'description': 'Zakres optymalny: <85°C\n• <85°C: Normalny\n• 85-95°C: Wysoki (Monitoruj)\n• >95°C: Krytyczny (Ryzyko uszkodzenia)',
            },
            Language.DUTCH: {
                'description': 'Optimaal bereik: <85°C\n• <85°C: Normaal\n• 85-95°C: Hoog (Monitor systeem)\n• >95°C: Kritisch (Risico op schade)',
            },
            Language.GERMAN: {
                'description': 'Optimalbereich: <85°C\n• <85°C: Normal\n• 85-95°C: Hoch (System überwachen)\n• >95°C: Kritisch (Schadensgefahr)',
            },
            Language.FRENCH: {
                'description': 'Plage optimale: <85°C\n• <85°C: Normal\n• 85-95°C: Élevé (surveiller le système)\n• >95°C: Critique (risque de dommage)',
            }
        },
        'cop': {
            Language.ENGLISH: {
                'description': 'Expected range: 4.0-4.5\n• <3.5: Poor efficiency\n• 3.5-4.0: Low\n• 4.0-4.5: Normal\n• 4.5-5.0: Good\n• >5.0: Excellent',
            },
            Language.POLISH: {
                'description': 'Zakres oczekiwany: 4.0-4.5\n• <3.5: Słaba wydajność\n• 3.5-4.0: Niska\n• 4.0-4.5: Normalna\n• 4.5-5.0: Dobra\n• >5.0: Doskonała',
            },
            Language.DUTCH: {
                'description': 'Verwacht bereik: 4.0-4.5\n• <3.5: Slechte efficiëntie\n• 3.5-4.0: Laag\n• 4.0-4.5: Normaal\n• 4.5-5.0: Goed\n• >5.0: Uitstekend',
            },
            Language.GERMAN: {
                'description': 'Erwarteter Bereich: 4.0-4.5\n• <3.5: Schlechte Effizienz\n• 3.5-4.0: Niedrig\n• 4.0-4.5: Normal\n• 4.5-5.0: Gut\n• >5.0: Hervorragend',
            },
            Language.FRENCH: {
                'description': 'Plage attendue: 4.0-4.5\n• <3.5: Faible efficacité\n• 3.5-4.0: Bas\n• 4.0-4.5: Normal\n• 4.5-5.0: Bon\n• >5.0: Excellent',
            }
        },
        'pump_speed': {
            Language.ENGLISH: {
                'description': 'Normal range: 40-80%\n• <40%: Low (Check flow)\n• 40-80%: Normal operation\n• >80%: High (Check system load)',
            },
            Language.POLISH: {
                'description': 'Zakres normalny: 40-80%\n• <40%: Niski (Sprawdź przepływ)\n• 40-80%: Normalna praca\n• >80%: Wysoki (Sprawdź obciążenie)',
            },
            Language.DUTCH: {
                'description': 'Normaal bereik: 40-80%\n• <40%: Laag (Controleer flow)\n• 40-80%: Normale werking\n• >80%: Hoog (Controleer belasting)',
            },
            Language.GERMAN: {
                'description': 'Normalbereich: 40-80%\n• <40%: Niedrig (Durchfluss prüfen)\n• 40-80%: Normalbetrieb\n• >80%: Hoch (Systemlast prüfen)',
            },
            Language.FRENCH: {
                'description': 'Plage normale: 40-80%\n• <40%: Faible (vérifier le débit)\n• 40-80%: Normal\n• >80%: Élevé (vérifier la charge du système)',
            }
        },
        'brine_temp_diff': {
            Language.ENGLISH: {
                'description': 'Optimal range: 3-4K\n• <2K: Low (Flow too high)\n• 2-3K: Low efficiency\n• 3-4K: Normal\n• >4K: High (Check flow rate)',
            },
            Language.POLISH: {
                'description': 'Zakres optymalny: 3-4K\n• <2K: Niski (Za wysoki przepływ)\n• 2-3K: Niska wydajność\n• 3-4K: Normalny\n• >4K: Wysoki (Sprawdź przepływ)',
            },
            Language.DUTCH: {
                'description': 'Optimaal bereik: 3-4K\n• <2K: Laag (Flow te hoog)\n• 2-3K: Lage efficiëntie\n• 3-4K: Normaal\n• >4K: Hoog (Controleer flow)',
            },
            Language.GERMAN: {
                'description': 'Optimalbereich: 3-4K\n• <2K: Niedrig (Zu hoher Durchfluss)\n• 2-3K: Geringe Effizienz\n• 3-4K: Normal\n• >4K: Hoch (Durchflussrate prüfen)',
            },
            Language.FRENCH: {
                'description': 'Plage optimale: 3-4K\n• <2K: Faible (débit trop élevé)\n• 2-3K: Faible efficacité\n• 3-4K: Normal\n• >4K: Élevé (vérifier le débit)',
            }
        },
        'heating_temp_diff': {
            Language.ENGLISH: {
                'description': 'Optimal range: 5-7K\n• <4K: Low (Flow too high)\n• 4-5K: Low efficiency\n• 5-7K: Normal\n• >7K: High (Check flow rate)',
            },
            Language.POLISH: {
                'description': 'Zakres optymalny: 5-7K\n• <4K: Niski (Za wysoki przepływ)\n• 4-5K: Niska wydajność\n• 5-7K: Normalny\n• >7K: Wysoki (Sprawdź przepływ)',
            },
            Language.DUTCH: {
                'description': 'Optimaal bereik: 5-7K\n• <4K: Laag (Flow te hoog)\n• 4-5K: Lage efficiëntie\n• 5-7K: Normaal\n• >7K: Hoog (Controleer flow)',
            },
            Language.GERMAN: {
                'description': 'Optimalbereich: 5-7K\n• <4K: Niedrig (Zu hoher Durchfluss)\n• 4-5K: Geringe Effizienz\n• 5-7K: Normal\n• >7K: Hoch (Durchflussrate prüfen)',
            },
            Language.FRENCH: {
                'description': 'Plage optimale: 5-7K\n• <4K: Faible (débit trop élevé)\n• 4-5K: Faible efficacité\n• 5-7K: Normal\n• >7K: Élevé (vérifier le débit)',
            }
        }
    }
}
