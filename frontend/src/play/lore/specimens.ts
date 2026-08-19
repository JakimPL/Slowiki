import type {
    Aspect,
    Case,
    Gender,
    GrammaticalNumber,
    InflectedForm,
    Inflection,
    LoreReading,
    Person,
    Tense,
    WordLore,
} from "../../api/lore";
import { inflectedBy } from "./bundle";

const CASES: readonly Case[] = ["mianownik", "dopełniacz", "celownik", "biernik", "narzędnik", "miejscownik", "wołacz"];

const PERSONS: readonly Person[] = ["pierwsza", "druga", "trzecia"];

const MASCULINE: readonly Gender[] = ["męskoosobowy", "męskozwierzęcy", "męskorzeczowy"];

const NON_MASCULINE: readonly Gender[] = ["męskozwierzęcy", "męskorzeczowy", "żeński", "nijaki"];

const IMPERFECT: readonly Aspect[] = ["niedokonany"];

function form(text: string, stated: Partial<Inflection>): InflectedForm {
    return { text, tags: inflectedBy(stated), playable: true };
}

function byCase(texts: Record<Case, string>, number: GrammaticalNumber, gender: Gender): readonly InflectedForm[] {
    return CASES.map((grammaticalCase) =>
        form(texts[grammaticalCase], { cases: [grammaticalCase], numbers: [number], genders: [gender] }),
    );
}

function nounForms(
    gender: Gender,
    singular: Record<Case, string>,
    plural: Record<Case, string>,
): readonly InflectedForm[] {
    return [...byCase(singular, "pojedyncza", gender), ...byCase(plural, "mnoga", gender)];
}

function byPerson(
    texts: Record<Person, string>,
    number: GrammaticalNumber,
    tense: Tense,
    aspects: readonly Aspect[],
): readonly InflectedForm[] {
    return PERSONS.map((person) =>
        form(texts[person], {
            verb_form: "forma osobowa",
            mood: "oznajmujący",
            tense,
            person,
            numbers: [number],
            aspects,
        }),
    );
}

function past(
    text: string,
    genders: readonly Gender[],
    number: GrammaticalNumber,
    aspects: readonly Aspect[],
): InflectedForm {
    return form(text, {
        verb_form: "forma przeszła",
        mood: "oznajmujący",
        tense: "przeszły",
        genders,
        numbers: [number],
        aspects,
    });
}

function imperative(
    text: string,
    person: Person,
    number: GrammaticalNumber,
    aspects: readonly Aspect[],
): InflectedForm {
    return form(text, { verb_form: "rozkaźnik", mood: "rozkazujący", person, numbers: [number], aspects });
}

function participle(
    text: string,
    verbForm: "imiesłów czynny" | "imiesłów bierny",
    grammaticalCase: Case,
    gender: Gender,
    number: GrammaticalNumber,
    negation: boolean,
): InflectedForm {
    return form(text, {
        verb_form: verbForm,
        cases: [grammaticalCase],
        genders: [gender],
        numbers: [number],
        negation,
        aspects: IMPERFECT,
    });
}

function gerund(text: string, grammaticalCase: Case, number: GrammaticalNumber): InflectedForm {
    return form(text, {
        verb_form: "odsłownik",
        cases: [grammaticalCase],
        genders: ["nijaki"],
        numbers: [number],
        aspects: IMPERFECT,
    });
}

function withoutDictionaryEntry(forms: readonly InflectedForm[], missing: readonly string[]): readonly InflectedForm[] {
    const refused = new Set(missing);
    return forms.map((one) => (refused.has(one.text) ? { ...one, playable: false } : one));
}

const SAW: LoreReading = {
    lexeme: "rzeczownik:PIŁA:SF",
    part: "rzeczownik",
    base: "PIŁA",
    forms: withoutDictionaryEntry(
        nounForms(
            "żeński",
            {
                mianownik: "PIŁA",
                dopełniacz: "PIŁY",
                celownik: "PILE",
                biernik: "PIŁĘ",
                narzędnik: "PIŁĄ",
                miejscownik: "PILE",
                wołacz: "PIŁO",
            },
            {
                mianownik: "PIŁY",
                dopełniacz: "PIŁ",
                celownik: "PIŁOM",
                biernik: "PIŁY",
                narzędnik: "PIŁAMI",
                miejscownik: "PIŁACH",
                wołacz: "PIŁY",
            },
        ),
        ["PIŁO"],
    ),
};

const DRINK: LoreReading = {
    lexeme: "czasownik:PIĆ:V",
    part: "czasownik",
    base: "PIĆ",
    forms: [
        form("PIĆ", { verb_form: "bezokolicznik", aspects: IMPERFECT }),
        ...byPerson({ pierwsza: "PIJĘ", druga: "PIJESZ", trzecia: "PIJE" }, "pojedyncza", "teraźniejszy", IMPERFECT),
        ...byPerson({ pierwsza: "PIJEMY", druga: "PIJECIE", trzecia: "PIJĄ" }, "mnoga", "teraźniejszy", IMPERFECT),
        past("PIŁ", MASCULINE, "pojedyncza", IMPERFECT),
        past("PIŁA", ["żeński"], "pojedyncza", IMPERFECT),
        past("PIŁO", ["nijaki"], "pojedyncza", IMPERFECT),
        past("PILI", ["męskoosobowy"], "mnoga", IMPERFECT),
        past("PIŁY", NON_MASCULINE, "mnoga", IMPERFECT),
        imperative("PIJ", "druga", "pojedyncza", IMPERFECT),
        imperative("PIJMY", "pierwsza", "mnoga", IMPERFECT),
        imperative("PIJCIE", "druga", "mnoga", IMPERFECT),
        form("PIJĄC", { verb_form: "imiesłów współczesny", aspects: IMPERFECT }),
        gerund("PICIE", "mianownik", "pojedyncza"),
        gerund("PICIA", "dopełniacz", "pojedyncza"),
    ],
};

const CASTLE: LoreReading = {
    lexeme: "rzeczownik:ZAMEK:SM3",
    part: "rzeczownik",
    base: "ZAMEK",
    forms: nounForms(
        "męskorzeczowy",
        {
            mianownik: "ZAMEK",
            dopełniacz: "ZAMKU",
            celownik: "ZAMKOWI",
            biernik: "ZAMEK",
            narzędnik: "ZAMKIEM",
            miejscownik: "ZAMKU",
            wołacz: "ZAMKU",
        },
        {
            mianownik: "ZAMKI",
            dopełniacz: "ZAMKÓW",
            celownik: "ZAMKOM",
            biernik: "ZAMKI",
            narzędnik: "ZAMKAMI",
            miejscownik: "ZAMKACH",
            wołacz: "ZAMKI",
        },
    ),
};

const HOUSE: LoreReading = {
    lexeme: "rzeczownik:DOM:SM3",
    part: "rzeczownik",
    base: "DOM",
    forms: nounForms(
        "męskorzeczowy",
        {
            mianownik: "DOM",
            dopełniacz: "DOMU",
            celownik: "DOMOWI",
            biernik: "DOM",
            narzędnik: "DOMEM",
            miejscownik: "DOMU",
            wołacz: "DOMU",
        },
        {
            mianownik: "DOMY",
            dopełniacz: "DOMÓW",
            celownik: "DOMOM",
            biernik: "DOMY",
            narzędnik: "DOMAMI",
            miejscownik: "DOMACH",
            wołacz: "DOMY",
        },
    ),
};

const CAT: LoreReading = {
    lexeme: "rzeczownik:KOT:SM2",
    part: "rzeczownik",
    base: "KOT",
    forms: nounForms(
        "męskozwierzęcy",
        {
            mianownik: "KOT",
            dopełniacz: "KOTA",
            celownik: "KOTU",
            biernik: "KOTA",
            narzędnik: "KOTEM",
            miejscownik: "KOCIE",
            wołacz: "KOCIE",
        },
        {
            mianownik: "KOTY",
            dopełniacz: "KOTÓW",
            celownik: "KOTOM",
            biernik: "KOTY",
            narzędnik: "KOTAMI",
            miejscownik: "KOTACH",
            wołacz: "KOTY",
        },
    ),
};

const WEAPON: LoreReading = {
    lexeme: "rzeczownik:BROŃ:SF",
    part: "rzeczownik",
    base: "BROŃ",
    forms: nounForms(
        "żeński",
        {
            mianownik: "BROŃ",
            dopełniacz: "BRONI",
            celownik: "BRONI",
            biernik: "BROŃ",
            narzędnik: "BRONIĄ",
            miejscownik: "BRONI",
            wołacz: "BRONI",
        },
        {
            mianownik: "BRONIE",
            dopełniacz: "BRONI",
            celownik: "BRONIOM",
            biernik: "BRONIE",
            narzędnik: "BRONIAMI",
            miejscownik: "BRONIACH",
            wołacz: "BRONIE",
        },
    ),
};

const DEFEND: LoreReading = {
    lexeme: "czasownik:BRONIĆ:V",
    part: "czasownik",
    base: "BRONIĆ",
    forms: [
        form("BRONIĆ", { verb_form: "bezokolicznik", aspects: IMPERFECT }),
        ...byPerson(
            { pierwsza: "BRONIĘ", druga: "BRONISZ", trzecia: "BRONI" },
            "pojedyncza",
            "teraźniejszy",
            IMPERFECT,
        ),
        ...byPerson({ pierwsza: "BRONIMY", druga: "BRONICIE", trzecia: "BRONIĄ" }, "mnoga", "teraźniejszy", IMPERFECT),
        past("BRONIŁ", MASCULINE, "pojedyncza", IMPERFECT),
        past("BRONIŁA", ["żeński"], "pojedyncza", IMPERFECT),
        past("BRONIŁO", ["nijaki"], "pojedyncza", IMPERFECT),
        past("BRONILI", ["męskoosobowy"], "mnoga", IMPERFECT),
        past("BRONIŁY", NON_MASCULINE, "mnoga", IMPERFECT),
        imperative("BROŃ", "druga", "pojedyncza", IMPERFECT),
        form("BRONIĄC", { verb_form: "imiesłów współczesny", aspects: IMPERFECT }),
    ],
};

const ROAD: LoreReading = {
    lexeme: "rzeczownik:DROGA:SF",
    part: "rzeczownik",
    base: "DROGA",
    forms: nounForms(
        "żeński",
        {
            mianownik: "DROGA",
            dopełniacz: "DROGI",
            celownik: "DRODZE",
            biernik: "DROGĘ",
            narzędnik: "DROGĄ",
            miejscownik: "DRODZE",
            wołacz: "DROGO",
        },
        {
            mianownik: "DROGI",
            dopełniacz: "DRÓG",
            celownik: "DROGOM",
            biernik: "DROGI",
            narzędnik: "DROGAMI",
            miejscownik: "DROGACH",
            wołacz: "DROGI",
        },
    ),
};

const EXPENSIVE: LoreReading = {
    lexeme: "przymiotnik:DROGI:ADJ",
    part: "przymiotnik",
    base: "DROGI",
    forms: [
        form("DROGI", {
            cases: ["mianownik"],
            numbers: ["pojedyncza"],
            genders: ["męskoosobowy"],
            degree: "równy",
        }),
        form("DROGIEGO", {
            cases: ["dopełniacz"],
            numbers: ["pojedyncza"],
            genders: ["męskoosobowy"],
            degree: "równy",
        }),
        form("DROGIM", {
            cases: ["narzędnik"],
            numbers: ["pojedyncza"],
            genders: ["męskoosobowy"],
            degree: "równy",
        }),
        form("DROGA", { cases: ["mianownik"], numbers: ["pojedyncza"], genders: ["żeński"], degree: "równy" }),
        form("DROGIEJ", { cases: ["dopełniacz"], numbers: ["pojedyncza"], genders: ["żeński"], degree: "równy" }),
        form("DROGĄ", { cases: ["narzędnik"], numbers: ["pojedyncza"], genders: ["żeński"], degree: "równy" }),
        form("DRODZY", { cases: ["mianownik"], numbers: ["mnoga"], genders: ["męskoosobowy"], degree: "równy" }),
        form("DROŻSZY", {
            cases: ["mianownik"],
            numbers: ["pojedyncza"],
            genders: ["męskoosobowy"],
            degree: "wyższy",
        }),
    ],
};

const WRITE: LoreReading = {
    lexeme: "czasownik:PISAĆ:V",
    part: "czasownik",
    base: "PISAĆ",
    forms: [
        form("PISAĆ", { verb_form: "bezokolicznik", aspects: IMPERFECT }),
        ...byPerson({ pierwsza: "PISZĘ", druga: "PISZESZ", trzecia: "PISZE" }, "pojedyncza", "teraźniejszy", IMPERFECT),
        ...byPerson({ pierwsza: "PISZEMY", druga: "PISZECIE", trzecia: "PISZĄ" }, "mnoga", "teraźniejszy", IMPERFECT),
        past("PISAŁ", MASCULINE, "pojedyncza", IMPERFECT),
        past("PISAŁA", ["żeński"], "pojedyncza", IMPERFECT),
        past("PISAŁO", ["nijaki"], "pojedyncza", IMPERFECT),
        past("PISALI", ["męskoosobowy"], "mnoga", IMPERFECT),
        past("PISAŁY", NON_MASCULINE, "mnoga", IMPERFECT),
        imperative("PISZ", "druga", "pojedyncza", IMPERFECT),
        imperative("PISZMY", "pierwsza", "mnoga", IMPERFECT),
        imperative("PISZCIE", "druga", "mnoga", IMPERFECT),
        form("PISANO", { verb_form: "bezosobnik", aspects: IMPERFECT }),
        participle("PISZĄCY", "imiesłów czynny", "mianownik", "męskoosobowy", "pojedyncza", false),
        participle("PISZĄCA", "imiesłów czynny", "mianownik", "żeński", "pojedyncza", false),
        participle("PISANY", "imiesłów bierny", "mianownik", "męskorzeczowy", "pojedyncza", false),
        participle("PISANA", "imiesłów bierny", "mianownik", "żeński", "pojedyncza", false),
        participle("PISANI", "imiesłów bierny", "mianownik", "męskoosobowy", "mnoga", false),
        participle("NIEPISANY", "imiesłów bierny", "mianownik", "męskorzeczowy", "pojedyncza", true),
        form("PISZĄC", { verb_form: "imiesłów współczesny", aspects: IMPERFECT }),
        gerund("PISANIE", "mianownik", "pojedyncza"),
        gerund("PISANIA", "dopełniacz", "pojedyncza"),
    ],
};

const SPECIMENS: readonly WordLore[] = [
    { word: "PIŁA", playable: true, readings: [SAW, DRINK] },
    { word: "ZAMEK", playable: true, readings: [CASTLE] },
    { word: "DOM", playable: true, readings: [HOUSE] },
    { word: "KOT", playable: true, readings: [CAT] },
    { word: "BRONIĄ", playable: true, readings: [WEAPON, DEFEND] },
    { word: "DROGĄ", playable: true, readings: [ROAD, EXPENSIVE] },
    { word: "PISAĆ", playable: true, readings: [WRITE] },
    { word: "ĆWIR", playable: true, readings: [] },
];

const BY_WORD: ReadonlyMap<string, WordLore> = new Map(SPECIMENS.map((lore) => [lore.word, lore]));

export const SPECIMEN_WORDS: readonly string[] = SPECIMENS.map((lore) => lore.word);

export function specimenFor(word: string): WordLore | null {
    return BY_WORD.get(word) ?? null;
}
