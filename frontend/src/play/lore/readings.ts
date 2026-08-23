import type { InflectedForm, LoreReading, WordLore } from "../../api/lore";

export type LoreState = "absent" | "unclassified" | "read";

export type LoreProgress = "asking" | "ready" | "failed";

export interface ChosenReading {
    readonly readings: readonly LoreReading[];
    readonly reading: LoreReading;
}

export interface LoreAnswer {
    readonly state: LoreProgress;
    readonly lore: WordLore | null;
}

export const NO_LORE_ANSWER: LoreAnswer = { state: "asking", lore: null };

export function loreStateOf(lore: WordLore): LoreState {
    if (!lore.playable) {
        return "absent";
    }
    return lore.readings.length === 0 ? "unclassified" : "read";
}

export function askedFormsOf(reading: LoreReading, word: string): readonly InflectedForm[] {
    return reading.forms.filter((form) => form.text === word);
}

export function readingByLexeme(lore: WordLore, lexeme: string): LoreReading | null {
    return lore.readings.find((reading) => reading.lexeme === lexeme) ?? null;
}

export function chosenReading(answer: LoreAnswer, lexeme: string | null): ChosenReading | null {
    if (answer.state !== "ready" || answer.lore === null || lexeme === null) {
        return null;
    }
    const reading = readingByLexeme(answer.lore, lexeme);
    return reading === null ? null : { readings: answer.lore.readings, reading };
}

export function firstLexeme(lore: WordLore): string | null {
    return lore.readings[0]?.lexeme ?? null;
}
