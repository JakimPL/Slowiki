from typing import Final

from lexica.grammar.aspect import Aspect
from lexica.grammar.case import Case
from lexica.grammar.degree import Degree
from lexica.grammar.gender import Gender
from lexica.grammar.number import Number
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.grammar.person import Person
from lexica.grammar.quality import Quality
from lexica.grammar.segments import SegmentTable

UNSPECIFIED_GENDER: Final = "_"

POLIMORF_SEGMENTS: Final = SegmentTable(
    parts={
        "subst": PartOfSpeech.RZECZOWNIK,
        "depr": PartOfSpeech.RZECZOWNIK,
        "adj": PartOfSpeech.PRZYMIOTNIK,
        "adja": PartOfSpeech.PRZYMIOTNIK,
        "adjc": PartOfSpeech.PRZYMIOTNIK,
        "adjp": PartOfSpeech.PRZYMIOTNIK,
        "adv": PartOfSpeech.PRZYSŁÓWEK,
        "num": PartOfSpeech.LICZEBNIK,
        "ppron12": PartOfSpeech.ZAIMEK,
        "ppron3": PartOfSpeech.ZAIMEK,
        "prep": PartOfSpeech.PRZYIMEK,
        "conj": PartOfSpeech.SPÓJNIK,
        "comp": PartOfSpeech.SPÓJNIK,
        "qub": PartOfSpeech.PARTYKUŁA,
        "interj": PartOfSpeech.WYKRZYKNIK,
        "fin": PartOfSpeech.CZASOWNIK,
        "bedzie": PartOfSpeech.CZASOWNIK,
        "aglt": PartOfSpeech.CZASOWNIK,
        "praet": PartOfSpeech.CZASOWNIK,
        "impt": PartOfSpeech.CZASOWNIK,
        "imps": PartOfSpeech.CZASOWNIK,
        "inf": PartOfSpeech.CZASOWNIK,
        "pcon": PartOfSpeech.CZASOWNIK,
        "pant": PartOfSpeech.CZASOWNIK,
        "pact": PartOfSpeech.CZASOWNIK,
        "ppas": PartOfSpeech.CZASOWNIK,
        "ger": PartOfSpeech.CZASOWNIK,
        "winien": PartOfSpeech.CZASOWNIK,
        "pred": PartOfSpeech.CZASOWNIK,
        "burk": PartOfSpeech.INNY,
    },
    cases={
        "nom": Case.MIANOWNIK,
        "gen": Case.DOPEŁNIACZ,
        "dat": Case.CELOWNIK,
        "acc": Case.BIERNIK,
        "inst": Case.NARZĘDNIK,
        "loc": Case.MIEJSCOWNIK,
        "voc": Case.WOŁACZ,
    },
    numbers={
        "sg": Number.POJEDYNCZA,
        "pl": Number.MNOGA,
    },
    genders={
        "m1": frozenset({Gender.MĘSKOOSOBOWY}),
        "m2": frozenset({Gender.MĘSKOZWIERZĘCY}),
        "m3": frozenset({Gender.MĘSKORZECZOWY}),
        "f": frozenset({Gender.ŻEŃSKI}),
        "n1": frozenset({Gender.NIJAKI}),
        "n2": frozenset({Gender.NIJAKI}),
        "p1": frozenset({Gender.MĘSKOOSOBOWY}),
        "p2": frozenset({Gender.NIJAKI}),
        "p3": frozenset({Gender.NIJAKI}),
        UNSPECIFIED_GENDER: frozenset(),
    },
    persons={
        "pri": Person.PIERWSZA,
        "sec": Person.DRUGA,
        "ter": Person.TRZECIA,
    },
    aspects={
        "imperf": Aspect.NIEDOKONANY,
        "perf": Aspect.DOKONANY,
    },
    degrees={
        "pos": Degree.RÓWNY,
        "com": Degree.WYŻSZY,
        "sup": Degree.NAJWYŻSZY,
    },
    qualities={
        "akc": Quality.AKCENTOWANY,
        "nakc": Quality.NIEAKCENTOWANY,
        "praep": Quality.POPRZYIMKOWY,
        "npraep": Quality.NIEPOPRZYIMKOWY,
        "agl": Quality.AGLUTYNACYJNY,
        "nagl": Quality.NIEAGLUTYNACYJNY,
        "wok": Quality.WOKALICZNY,
        "nwok": Quality.NIEWOKALICZNY,
        "congr": Quality.UZGADNIAJĄCY,
        "rec": Quality.RZĄDZĄCY,
        "comp": Quality.ZŁOŻONY,
    },
)
