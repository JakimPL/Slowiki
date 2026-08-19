import type { WordLore } from "../../api/lore";
import { specimenFor } from "./specimens";
import { synthesisFor } from "./synthesis";

export const SAMPLE_SOURCE = true;

export function loreFor(word: string, playable: boolean): WordLore {
    if (!playable) {
        return { word, playable: false, readings: [] };
    }
    return specimenFor(word) ?? synthesisFor(word);
}
