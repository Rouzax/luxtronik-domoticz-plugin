from enum import Enum, auto


class Language(Enum):
    """Supported languages"""
    ENGLISH = auto()
    POLISH = auto()
    DUTCH = auto()


# Define translations
TRANSLATIONS = {
    'Heat supply temp': {
        Language.POLISH: 'Temp zasilania',
        Language.DUTCH: 'Aanvoertemp verw'
    },
    'Heat return temp': {
        Language.POLISH: 'Temp powrotu',
        Language.DUTCH: 'Retourtemp verw'
    },
    'Return temp target': {
        Language.POLISH: 'Temp powr cel',
        Language.DUTCH: 'Retourtemp doel'
    },
    'Outside temp': {
        Language.POLISH: 'Temp zewn',
        Language.DUTCH: 'Buitentemp'
    },
    'Outside temp avg': {
        Language.POLISH: 'Temp zewn śred',
        Language.DUTCH: 'Buitentemp gem'
    },
    'DHW temp': {
        Language.POLISH: 'Temp cwu',
        Language.DUTCH: 'Temp tapwater'
    },
    'DHW temp target': {
        Language.POLISH: 'Temp cwu cel',
        Language.DUTCH: 'Tapwater inst'
    },
    'WP source in temp': {
        Language.POLISH: 'Temp WP źródło wej',
        Language.DUTCH: 'WP bron in temp'
    },
    'WP source out temp': {
        Language.POLISH: 'Temp WP źródło wyj',
        Language.DUTCH: 'WP bron uit temp'
    },
    'MC1 temp': {
        Language.POLISH: 'Temp OM1',
        Language.DUTCH: 'Menggroep1 temp'
    },
    'MC1 temp target': {
        Language.POLISH: 'Temp OM1 cel',
        Language.DUTCH: 'Menggroep1 inst'
    },
    'MC2 temp': {
        Language.POLISH: 'Temp OM2',
        Language.DUTCH: 'Menggroep2 temp'
    },
    'MC2 temp target': {
        Language.POLISH: 'Temp OM2 cel',
        Language.DUTCH: 'Menggroep2 inst'
    },
    'Heating mode': {
        Language.POLISH: 'Obieg grzewczy',
        Language.DUTCH: 'Verwarmen'
    },
    'Hot water mode': {
        Language.POLISH: 'Woda użytkowa',
        Language.DUTCH: 'Warmwater'
    },
    'Cooling': {
        Language.POLISH: 'Chłodzenie',
        Language.DUTCH: 'Koeling'
    },
    'Automatic': {
        Language.POLISH: 'Automatyczny',
        Language.DUTCH: 'Automatisch'
    },
    '2nd heat source': {
        Language.POLISH: 'II źr. ciepła',
        Language.DUTCH: '2e warm.opwek'
    },
    'Party': {
        Language.POLISH: 'Party',
        Language.DUTCH: 'Party'
    },
    'Holidays': {
        Language.POLISH: 'Wakacje',
        Language.DUTCH: 'Vakantie'
    },
    'Off': {
        Language.POLISH: 'Wył.',
        Language.DUTCH: 'Uit'
    },
    'No requirement': {
        Language.POLISH: 'Brak zapotrzebowania',
        Language.DUTCH: 'Geen warmtevraag'
    },
    'Swimming pool mode / Photovoltaik': {
        Language.POLISH: 'Tryb basen / Fotowoltaika',
        Language.DUTCH: 'Zwembad / Fotovoltaïek'
    },
    'EVUM': {
        Language.POLISH: 'EVU',
        Language.DUTCH: 'EVU'
    },
    'Defrost': {
        Language.POLISH: 'Rozmrażanie',
        Language.DUTCH: 'Ontdooien'
    },
    'Heating external source mode': {
        Language.POLISH: 'Ogrzewanie z zewnętrznego źródła',
        Language.DUTCH: 'Verwarmen 2e warm.opwek'
    },
    'Temp +-': {
        Language.POLISH: 'Temp +-',
        Language.DUTCH: 'Temp +-'
    },
    'Working mode': {
        Language.POLISH: 'Stan pracy',
        Language.DUTCH: 'Bedrijfsmode'
    },
    'Flow': {
        Language.POLISH: 'Przepływ',
        Language.DUTCH: 'Debiet'
    },
    'Compressor freq': {
        Language.POLISH: 'Częst sprężarki',
        Language.DUTCH: 'Compr freq'
    },
    'Room temp': {
        Language.POLISH: 'Temp pokojowa',
        Language.DUTCH: 'Ruimtetemp act'
    },
    'Room temp target': {
        Language.POLISH: 'Temp pokoj cel',
        Language.DUTCH: 'Ruimtetemp gew'
    },
    'Power total': {
        Language.POLISH: 'Pobór mocy',
        Language.DUTCH: 'Energie totaal'
    },
    'Power heating': {
        Language.POLISH: 'Pobór grz',
        Language.DUTCH: 'Energie verw'
    },
    'Power DHW': {
        Language.POLISH: 'Pobór cwu',
        Language.DUTCH: 'Energie warmw'
    },
    'Heat out total': {
        Language.POLISH: 'Moc grz razem',
        Language.DUTCH: 'Verwarm totaal'
    },
    'Heat out heating': {
        Language.POLISH: 'Moc grz ogrz',
        Language.DUTCH: 'Verwarm verw'
    },
    'Heat out DHW': {
        Language.POLISH: 'Moc grz cwu',
        Language.DUTCH: 'Verwarm warmw'
    },
    'COP total': {
        Language.POLISH: 'COP razem',
        Language.DUTCH: 'COP totaal'
    },
    'Heating pump speed': {
        Language.POLISH: 'Pompa CO procent',
        Language.DUTCH: 'CV pomp snelheid'
    },
    'Brine pump speed': {
        Language.POLISH: 'Pompa DZ procent',
        Language.DUTCH: 'Bronpomp snelheid'
    },
    'Hot gas temp': {
        Language.POLISH: 'Temp gazu gorącego',
        Language.DUTCH: 'Heetgas temp'
    },
    'Suction temp': {
        Language.POLISH: 'Temp zasysania',
        Language.DUTCH: 'Aanzuig temp'
    },
    'Superheat': {
        Language.POLISH: 'Przegrzanie',
        Language.DUTCH: 'Oververhitting'
    },
    'High pressure': {
        Language.POLISH: 'Wysokie ciśnienie',
        Language.DUTCH: 'Hoge druk'
    },
    'Low pressure': {
        Language.POLISH: 'Niskie ciśnienie',
        Language.DUTCH: 'Lage druk'
    }
}
