from enum import StrEnum


class Case(StrEnum):
    MIANOWNIK = "mianownik"
    DOPEŁNIACZ = "dopełniacz"
    CELOWNIK = "celownik"
    BIERNIK = "biernik"
    NARZĘDNIK = "narzędnik"
    MIEJSCOWNIK = "miejscownik"
    WOŁACZ = "wołacz"


class Number(StrEnum):
    POJEDYNCZA = "pojedyncza"
    MNOGA = "mnoga"


class Gender(StrEnum):
    MĘSKOOSOBOWY = "męskoosobowy"
    MĘSKOZWIERZĘCY = "męskozwierzęcy"
    MĘSKORZECZOWY = "męskorzeczowy"
    ŻEŃSKI = "żeński"
    NIJAKI = "nijaki"


class Person(StrEnum):
    PIERWSZA = "pierwsza"
    DRUGA = "druga"
    TRZECIA = "trzecia"


class Tense(StrEnum):
    TERAŹNIEJSZY = "teraźniejszy"
    PRZESZŁY = "przeszły"
    PRZYSZŁY = "przyszły"


class Mood(StrEnum):
    OZNAJMUJĄCY = "oznajmujący"
    ROZKAZUJĄCY = "rozkazujący"
    PRZYPUSZCZAJĄCY = "przypuszczający"


class Aspect(StrEnum):
    DOKONANY = "dokonany"
    NIEDOKONANY = "niedokonany"


class Degree(StrEnum):
    RÓWNY = "równy"
    WYŻSZY = "wyższy"
    NAJWYŻSZY = "najwyższy"


class VerbForm(StrEnum):
    BEZOKOLICZNIK = "bezokolicznik"
    FORMA_OSOBOWA = "forma osobowa"
    FORMA_PRZESZŁA = "forma przeszła"
    ROZKAŹNIK = "rozkaźnik"
    BEZOSOBNIK = "bezosobnik"
    IMIESŁÓW_CZYNNY = "imiesłów czynny"
    IMIESŁÓW_BIERNY = "imiesłów bierny"
    IMIESŁÓW_WSPÓŁCZESNY = "imiesłów współczesny"
    IMIESŁÓW_UPRZEDNI = "imiesłów uprzedni"
    ODSŁOWNIK = "odsłownik"
    KOŃCÓWKA_RUCHOMA = "końcówka ruchoma"
    PREDYKATYW = "predykatyw"
    WINIEN = "winien"


class NumeralType(StrEnum):
    GŁÓWNY = "główny"
    PORZĄDKOWY = "porządkowy"
    ZBIOROWY = "zbiorowy"
    UŁAMKOWY = "ułamkowy"
    NIEOKREŚLONY = "nieokreślony"


class PronounType(StrEnum):
    OSOBOWY = "osobowy"
    ZWROTNY = "zwrotny"
    DZIERŻAWCZY = "dzierżawczy"
    WSKAZUJĄCY = "wskazujący"
    PYTAJNY = "pytajny"
    WZGLĘDNY = "względny"
    NIEOKREŚLONY = "nieokreślony"
    PRZECZĄCY = "przeczący"
