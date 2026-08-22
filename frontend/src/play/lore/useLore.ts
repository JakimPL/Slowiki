import { useMemo } from "react";

import type { AskedWord } from "../words/asked";
import { loreFor } from "./lore";
import type { LoreAnswer } from "./readings";
import { assumedPlayable, NO_LORE_ANSWER } from "./readings";

export function useLore(asked: AskedWord | null): LoreAnswer {
    const text = asked === null ? "" : asked.text;
    const playable = asked !== null && assumedPlayable(asked.status);
    return useMemo<LoreAnswer>(
        () => (text === "" ? NO_LORE_ANSWER : { state: "ready", lore: loreFor(text, playable) }),
        [text, playable],
    );
}
