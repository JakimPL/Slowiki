export type Part =
    | "rzeczownik"
    | "przymiotnik"
    | "czasownik"
    | "przysłówek"
    | "liczebnik"
    | "zaimek"
    | "przyimek"
    | "spójnik"
    | "partykuła"
    | "wykrzyknik"
    | "inny";

export type Case = "mianownik" | "dopełniacz" | "celownik" | "biernik" | "narzędnik" | "miejscownik" | "wołacz";

export type GrammaticalNumber = "pojedyncza" | "mnoga";

export type Gender = "męskoosobowy" | "męskozwierzęcy" | "męskorzeczowy" | "żeński" | "nijaki";

export type Person = "pierwsza" | "druga" | "trzecia";

export type Tense = "teraźniejszy" | "przeszły" | "przyszły";

export type Mood = "oznajmujący" | "rozkazujący" | "przypuszczający";

export type Aspect = "dokonany" | "niedokonany";

export type Degree = "równy" | "wyższy" | "najwyższy";

export type VerbForm =
    | "bezokolicznik"
    | "forma osobowa"
    | "forma przeszła"
    | "rozkaźnik"
    | "bezosobnik"
    | "imiesłów czynny"
    | "imiesłów bierny"
    | "imiesłów współczesny"
    | "imiesłów uprzedni"
    | "odsłownik"
    | "końcówka ruchoma"
    | "predykatyw"
    | "winien";

export type NumeralType = "główny" | "porządkowy" | "zbiorowy" | "ułamkowy" | "nieokreślony";

export type PronounType =
    "osobowy" | "zwrotny" | "dzierżawczy" | "wskazujący" | "pytajny" | "względny" | "nieokreślony" | "przeczący";

export interface Inflection {
    readonly cases: readonly Case[];
    readonly number: GrammaticalNumber | null;
    readonly genders: readonly Gender[];
    readonly person: Person | null;
    readonly tense: Tense | null;
    readonly mood: Mood | null;
    readonly aspects: readonly Aspect[];
    readonly degree: Degree | null;
    readonly verb_form: VerbForm | null;
    readonly numeral_type: NumeralType | null;
    readonly pronoun_type: PronounType | null;
    readonly negation: boolean | null;
    readonly deprecative: boolean;
}

export interface InflectedForm {
    readonly text: string;
    readonly tags: Inflection;
    readonly playable: boolean;
}

export interface LoreReading {
    readonly lexeme: string;
    readonly part: Part;
    readonly base: string;
    readonly forms: readonly InflectedForm[];
}

export interface WordLore {
    readonly word: string;
    readonly playable: boolean;
    readonly readings: readonly LoreReading[];
}

export interface WordLoreResponse {
    readonly lore: Readonly<Record<string, WordLore>>;
}
