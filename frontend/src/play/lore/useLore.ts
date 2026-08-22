import { useEffect, useState } from "react";

import { readWordLore } from "../../api/client";
import type { Seat } from "../../api/seat";
import type { AskedWord } from "../words/asked";
import type { LoreAnswer } from "./readings";
import { NO_LORE_ANSWER } from "./readings";

const FAILED_ANSWER: LoreAnswer = { state: "failed", lore: null };

export function useLore(seat: Seat, asked: AskedWord | null): LoreAnswer {
    const [answer, setAnswer] = useState<LoreAnswer>(NO_LORE_ANSWER);
    const text = asked === null ? "" : asked.text;

    useEffect(() => {
        setAnswer(NO_LORE_ANSWER);
        if (text === "") {
            return;
        }
        let awaited = true;
        void readWordLore(seat, [text])
            .then((response) => {
                if (awaited) {
                    const lore = response.lore[text];
                    setAnswer(lore === undefined ? FAILED_ANSWER : { state: "ready", lore });
                }
            })
            .catch(() => {
                if (awaited) {
                    setAnswer(FAILED_ANSWER);
                }
            });
        return (): void => {
            awaited = false;
        };
    }, [seat, text]);

    return answer;
}
