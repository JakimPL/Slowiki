import { useCallback, useRef, useState } from "react";

import { sendMove } from "../api/client";
import type { Move } from "../api/moves";
import { reasonOf, Refused, UNKNOWN_CODE } from "../api/refusal";
import type { Seat } from "../api/seat";
import { delivered } from "./sending";

export interface PlayHold {
    readonly busy: boolean;
    readonly notice: string | null;
    readonly noticeCode: string | null;
    readonly send: (move: Move, premove: boolean) => void;
}

export function usePlay(seat: Seat, baseSeq: number): PlayHold {
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState<string | null>(null);
    const [noticeCode, setNoticeCode] = useState<string | null>(null);
    const inFlight = useRef(false);

    const send = useCallback(
        (move: Move, premove: boolean): void => {
            if (inFlight.current) {
                return;
            }
            inFlight.current = true;
            setBusy(true);
            setNotice(null);
            setNoticeCode(null);
            void delivered(() => sendMove(seat, move, baseSeq, premove))
                .catch((trouble: unknown) => {
                    setNotice(reasonOf(trouble));
                    setNoticeCode(trouble instanceof Refused ? trouble.code : UNKNOWN_CODE);
                })
                .finally(() => {
                    inFlight.current = false;
                    setBusy(false);
                });
        },
        [seat, baseSeq],
    );

    return { busy, notice, noticeCode, send };
}
