import { useEffect, useState } from "react";

import { readWordVerdicts } from "../../api/client";
import type { Seat } from "../../api/seat";
import type { Judged } from "./verdicts";
import { NO_JUDGEMENTS, unjudged, withVerdicts } from "./verdicts";

const JUDGE_DELAY_MS = 220;
const ASKED_SEPARATOR = " ";

export function useJudgements(seat: Seat, texts: readonly string[], live: boolean): Judged {
    const [judged, setJudged] = useState<Judged>(NO_JUDGEMENTS);
    const asked = live ? unjudged(texts, judged).join(ASKED_SEPARATOR) : "";

    useEffect(() => {
        if (asked === "") {
            return;
        }
        const words = asked.split(ASKED_SEPARATOR);
        const timer = window.setTimeout(() => {
            void readWordVerdicts(seat, words)
                .then((answer) => {
                    setJudged((current) => withVerdicts(current, answer.verdicts));
                })
                .catch(() => undefined);
        }, JUDGE_DELAY_MS);
        return (): void => {
            window.clearTimeout(timer);
        };
    }, [asked, seat]);

    return judged;
}
