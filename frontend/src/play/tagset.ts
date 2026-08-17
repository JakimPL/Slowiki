import type {
    Aspect,
    Case,
    Degree,
    Gender,
    GrammaticalNumber,
    Mood,
    NumeralType,
    Part,
    Person,
    PronounType,
    Tense,
    VerbForm,
} from "../api/lore";

export const PART_ORDER: Record<Part, number> = {
    rzeczownik: 0,
    przymiotnik: 1,
    czasownik: 2,
    przysłówek: 3,
    liczebnik: 4,
    zaimek: 5,
    przyimek: 6,
    spójnik: 7,
    partykuła: 8,
    wykrzyknik: 9,
    inny: 10,
};

export const CASE_ORDER: Record<Case, number> = {
    mianownik: 0,
    dopełniacz: 1,
    celownik: 2,
    biernik: 3,
    narzędnik: 4,
    miejscownik: 5,
    wołacz: 6,
};

export const NUMBER_ORDER: Record<GrammaticalNumber, number> = {
    pojedyncza: 0,
    mnoga: 1,
};

export const GENDER_ORDER: Record<Gender, number> = {
    męskoosobowy: 0,
    męskozwierzęcy: 1,
    męskorzeczowy: 2,
    żeński: 3,
    nijaki: 4,
};

export const PERSON_ORDER: Record<Person, number> = {
    pierwsza: 0,
    druga: 1,
    trzecia: 2,
};

export const TENSE_ORDER: Record<Tense, number> = {
    teraźniejszy: 0,
    przeszły: 1,
    przyszły: 2,
};

export const MOOD_ORDER: Record<Mood, number> = {
    oznajmujący: 0,
    rozkazujący: 1,
    przypuszczający: 2,
};

export const ASPECT_ORDER: Record<Aspect, number> = {
    niedokonany: 0,
    dokonany: 1,
};

export const DEGREE_ORDER: Record<Degree, number> = {
    równy: 0,
    wyższy: 1,
    najwyższy: 2,
};

export const VERB_FORM_ORDER: Record<VerbForm, number> = {
    bezokolicznik: 0,
    "forma osobowa": 1,
    "forma przeszła": 2,
    rozkaźnik: 3,
    bezosobnik: 4,
    "imiesłów czynny": 5,
    "imiesłów bierny": 6,
    "imiesłów współczesny": 7,
    "imiesłów uprzedni": 8,
    odsłownik: 9,
    "końcówka ruchoma": 10,
    predykatyw: 11,
    winien: 12,
};

export const NUMERAL_TYPE_ORDER: Record<NumeralType, number> = {
    główny: 0,
    porządkowy: 1,
    zbiorowy: 2,
    ułamkowy: 3,
    nieokreślony: 4,
};

export const PRONOUN_TYPE_ORDER: Record<PronounType, number> = {
    osobowy: 0,
    zwrotny: 1,
    dzierżawczy: 2,
    wskazujący: 3,
    pytajny: 4,
    względny: 5,
    nieokreślony: 6,
    przeczący: 7,
};

export function inOrder<Term extends string>(terms: readonly Term[], order: Record<Term, number>): readonly Term[] {
    return [...terms].sort((one, other) => order[one] - order[other]);
}
