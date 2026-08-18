import type { InflectedForm, Inflection, Part, WordLore } from "../../api/lore";
import { inflectedBy } from "./bundle";

interface SyntheticEnding {
    readonly ending: string;
    readonly tags: Partial<Inflection>;
}

interface SyntheticShape {
    readonly part: Part;
    readonly baseEnding: string | null;
    readonly asked: Partial<Inflection>;
    readonly rest: readonly SyntheticEnding[];
}

const SAMPLE_PATTERN = "PRÓBKA";

const FINAL_VOWEL = /[AEIOUYĄĘÓ]$/u;

const PRESENT: Partial<Inflection> = {
    verb_form: "forma osobowa",
    mood: "oznajmujący",
    tense: "teraźniejszy",
    aspects: ["niedokonany"],
};

const PAST: Partial<Inflection> = {
    verb_form: "forma przeszła",
    mood: "oznajmujący",
    tense: "przeszły",
    aspects: ["niedokonany"],
};

const SYNTHETIC_NOUN: SyntheticShape = {
    part: "rzeczownik",
    baseEnding: null,
    asked: { cases: ["mianownik"], number: "pojedyncza", genders: ["żeński"] },
    rest: [
        { ending: "Y", tags: { cases: ["dopełniacz"], number: "pojedyncza", genders: ["żeński"] } },
        { ending: "E", tags: { cases: ["celownik", "miejscownik"], number: "pojedyncza", genders: ["żeński"] } },
        { ending: "Ę", tags: { cases: ["biernik"], number: "pojedyncza", genders: ["żeński"] } },
        { ending: "Ą", tags: { cases: ["narzędnik"], number: "pojedyncza", genders: ["żeński"] } },
        { ending: "O", tags: { cases: ["wołacz"], number: "pojedyncza", genders: ["żeński"] } },
        { ending: "Y", tags: { cases: ["mianownik", "biernik", "wołacz"], number: "mnoga", genders: ["żeński"] } },
        { ending: "", tags: { cases: ["dopełniacz"], number: "mnoga", genders: ["żeński"] } },
        { ending: "OM", tags: { cases: ["celownik"], number: "mnoga", genders: ["żeński"] } },
        { ending: "AMI", tags: { cases: ["narzędnik"], number: "mnoga", genders: ["żeński"] } },
        { ending: "ACH", tags: { cases: ["miejscownik"], number: "mnoga", genders: ["żeński"] } },
    ],
};

const SYNTHETIC_ADJECTIVE: SyntheticShape = {
    part: "przymiotnik",
    baseEnding: null,
    asked: { cases: ["mianownik"], number: "pojedyncza", genders: ["męskoosobowy"], degree: "równy" },
    rest: [
        {
            ending: "EGO",
            tags: { cases: ["dopełniacz"], number: "pojedyncza", genders: ["męskoosobowy"], degree: "równy" },
        },
        {
            ending: "EMU",
            tags: { cases: ["celownik"], number: "pojedyncza", genders: ["męskoosobowy"], degree: "równy" },
        },
        {
            ending: "YM",
            tags: { cases: ["narzędnik"], number: "pojedyncza", genders: ["męskoosobowy"], degree: "równy" },
        },
        { ending: "A", tags: { cases: ["mianownik"], number: "pojedyncza", genders: ["żeński"], degree: "równy" } },
        { ending: "EJ", tags: { cases: ["dopełniacz"], number: "pojedyncza", genders: ["żeński"], degree: "równy" } },
        { ending: "Ą", tags: { cases: ["narzędnik"], number: "pojedyncza", genders: ["żeński"], degree: "równy" } },
        { ending: "E", tags: { cases: ["mianownik"], number: "pojedyncza", genders: ["nijaki"], degree: "równy" } },
        { ending: "I", tags: { cases: ["mianownik"], number: "mnoga", genders: ["męskoosobowy"], degree: "równy" } },
        {
            ending: "SZY",
            tags: { cases: ["mianownik"], number: "pojedyncza", genders: ["męskoosobowy"], degree: "wyższy" },
        },
    ],
};

const SYNTHETIC_VERB: SyntheticShape = {
    part: "czasownik",
    baseEnding: "AĆ",
    asked: { ...PRESENT, person: "trzecia", number: "pojedyncza" },
    rest: [
        { ending: "AĆ", tags: { verb_form: "bezokolicznik", aspects: ["niedokonany"] } },
        { ending: "Ę", tags: { ...PRESENT, person: "pierwsza", number: "pojedyncza" } },
        { ending: "ESZ", tags: { ...PRESENT, person: "druga", number: "pojedyncza" } },
        { ending: "EMY", tags: { ...PRESENT, person: "pierwsza", number: "mnoga" } },
        { ending: "ECIE", tags: { ...PRESENT, person: "druga", number: "mnoga" } },
        { ending: "Ą", tags: { ...PRESENT, person: "trzecia", number: "mnoga" } },
        {
            ending: "AŁ",
            tags: { ...PAST, genders: ["męskoosobowy", "męskozwierzęcy", "męskorzeczowy"], number: "pojedyncza" },
        },
        { ending: "AŁA", tags: { ...PAST, genders: ["żeński"], number: "pojedyncza" } },
        { ending: "AŁO", tags: { ...PAST, genders: ["nijaki"], number: "pojedyncza" } },
        { ending: "ALI", tags: { ...PAST, genders: ["męskoosobowy"], number: "mnoga" } },
        {
            ending: "AŁY",
            tags: { ...PAST, genders: ["męskozwierzęcy", "męskorzeczowy", "żeński", "nijaki"], number: "mnoga" },
        },
        { ending: "AJĄC", tags: { verb_form: "imiesłów współczesny", aspects: ["niedokonany"] } },
    ],
};

const SHAPES: readonly SyntheticShape[] = [SYNTHETIC_NOUN, SYNTHETIC_ADJECTIVE, SYNTHETIC_VERB];

export function synthesisFor(word: string): WordLore {
    const shape = shapeFor(word);
    const stem = word.replace(FINAL_VOWEL, "");
    const base = shape.baseEnding === null ? word : stem + shape.baseEnding;
    const asked: InflectedForm = { text: word, tags: inflectedBy(shape.asked), playable: true };
    const fabricated = shape.rest
        .map((one) => ({ text: stem + one.ending, tags: inflectedBy(one.tags), playable: false }))
        .filter((one) => one.text !== word);
    return {
        word,
        playable: true,
        readings: [
            {
                lexeme: `${shape.part}:${base}:${SAMPLE_PATTERN}`,
                part: shape.part,
                base,
                forms: [asked, ...fabricated],
            },
        ],
    };
}

function shapeFor(word: string): SyntheticShape {
    return SHAPES[letterSum(word) % SHAPES.length] ?? SYNTHETIC_NOUN;
}

function letterSum(word: string): number {
    let sum = 0;
    for (const letter of word) {
        sum += letter.codePointAt(0) ?? 0;
    }
    return sum;
}
