import { useMemo } from "react";

import type { WordChip } from "./chips";
import { loreFor, SAMPLE_SOURCE } from "./lore";
import type { LoreAnswer } from "./readings";
import { assumedPlayable, NO_LORE_ANSWER } from "./readings";

export function useLore(chip: WordChip | null): LoreAnswer {
    const text = chip === null ? "" : chip.text;
    const playable = chip !== null && assumedPlayable(chip.status);
    return useMemo<LoreAnswer>(
        () => (text === "" ? NO_LORE_ANSWER : { state: "ready", lore: loreFor(text, playable), sample: SAMPLE_SOURCE }),
        [text, playable],
    );
}
