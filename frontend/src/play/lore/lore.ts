import type { WordLore } from "../../api/lore";

export function loreFor(word: string, playable: boolean): WordLore {
    return { word, playable, readings: [] };
}
