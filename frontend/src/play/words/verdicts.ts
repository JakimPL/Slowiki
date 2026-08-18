import type { WordVerdict } from "../../api/words";

export type Judged = ReadonlyMap<string, boolean>;

export const NO_JUDGEMENTS: Judged = new Map();

export function unjudged(texts: readonly string[], judged: Judged): readonly string[] {
    return [...new Set(texts.filter((text) => text !== "" && !judged.has(text)))];
}

export function withVerdicts(judged: Judged, verdicts: Readonly<Record<string, WordVerdict>>): Judged {
    const merged = new Map(judged);
    for (const [word, verdict] of Object.entries(verdicts)) {
        merged.set(word, verdict.allowed);
    }
    return merged;
}
