import type {
    Aspect,
    Case,
    Degree,
    Gender,
    GrammaticalNumber,
    Inflection,
    Mood,
    NumeralType,
    Part,
    Person,
    PronounType,
    Tense,
    VerbForm,
} from "../../api/lore";

export type Dimension =
    | "verbForm"
    | "numeralType"
    | "pronounType"
    | "mood"
    | "tense"
    | "aspect"
    | "person"
    | "case"
    | "number"
    | "gender"
    | "degree"
    | "negation"
    | "deprecative";

export const NEGATED_TERM = "zaprzeczony";

export const DEPRECATIVE_TERM = "deprecjatywny";

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

export const DIMENSION_ORDER: readonly Dimension[] = [
    "verbForm",
    "numeralType",
    "pronounType",
    "mood",
    "tense",
    "aspect",
    "person",
    "case",
    "number",
    "gender",
    "degree",
    "negation",
    "deprecative",
];

const ABSENT_RANK = -1;

const RANKS_ON: Record<Dimension, Readonly<Record<string, number>>> = {
    verbForm: VERB_FORM_ORDER,
    numeralType: NUMERAL_TYPE_ORDER,
    pronounType: PRONOUN_TYPE_ORDER,
    mood: MOOD_ORDER,
    tense: TENSE_ORDER,
    aspect: ASPECT_ORDER,
    person: PERSON_ORDER,
    case: CASE_ORDER,
    number: NUMBER_ORDER,
    gender: GENDER_ORDER,
    degree: DEGREE_ORDER,
    negation: { [NEGATED_TERM]: 0 },
    deprecative: { [DEPRECATIVE_TERM]: 0 },
};

const TERMS_ON: Record<Dimension, (tags: Inflection) => readonly string[]> = {
    verbForm: (tags) => stated(tags.verb_form),
    numeralType: (tags) => stated(tags.numeral_type),
    pronounType: (tags) => stated(tags.pronoun_type),
    mood: (tags) => stated(tags.mood),
    tense: (tags) => stated(tags.tense),
    aspect: (tags) => tags.aspects,
    person: (tags) => stated(tags.person),
    case: (tags) => tags.cases,
    number: (tags) => stated(tags.number),
    gender: (tags) => tags.genders,
    degree: (tags) => stated(tags.degree),
    negation: (tags) => (tags.negation === true ? [NEGATED_TERM] : []),
    deprecative: (tags) => (tags.deprecative ? [DEPRECATIVE_TERM] : []),
};

export function inOrder<Term extends string>(terms: readonly Term[], order: Record<Term, number>): readonly Term[] {
    return [...terms].sort((one, other) => order[one] - order[other]);
}

export function orderedTerms(terms: readonly string[], dimension: Dimension): readonly string[] {
    return inOrder(terms, RANKS_ON[dimension]);
}

export function termsOn(tags: Inflection, dimension: Dimension): readonly string[] {
    return orderedTerms(TERMS_ON[dimension](tags), dimension);
}

export function compareInflections(one: Inflection, other: Inflection): number {
    for (const dimension of DIMENSION_ORDER) {
        const apart = leadingRank(one, dimension) - leadingRank(other, dimension);
        if (apart !== 0) {
            return apart;
        }
    }
    return 0;
}

function leadingRank(tags: Inflection, dimension: Dimension): number {
    const leading = termsOn(tags, dimension)[0];
    return leading === undefined ? ABSENT_RANK : (RANKS_ON[dimension][leading] ?? ABSENT_RANK);
}

function stated(term: string | null): readonly string[] {
    return term === null ? [] : [term];
}
