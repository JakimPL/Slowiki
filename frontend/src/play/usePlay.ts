import { useCallback, useEffect, useRef, useState } from "react";

import { cancelPremove, sendMove } from "../api/client";
import type { Move } from "../api/moves";
import { NO_PREMOVE_CODE, reasonOf, Refused, STALE_POSITION_CODE, UNKNOWN_CODE } from "../api/refusal";
import type { Seat } from "../api/seat";
import { delivered } from "./sending";

export interface PlayHold {
    readonly busy: boolean;
    readonly notice: string | null;
    readonly noticeCode: string | null;
    readonly send: (move: Move, premove: boolean) => void;
    readonly revoke: () => void;
    readonly clear: () => void;
}

const ECHO_TIMEOUT_MS = 4000;

export function usePlay(seat: Seat, baseSeq: number, onOutdated: () => Promise<number | null>): PlayHold {
    const [sending, setSending] = useState(false);
    const [awaitedSeq, setAwaitedSeq] = useState<number | null>(null);
    const [notice, setNotice] = useState<string | null>(null);
    const [noticeCode, setNoticeCode] = useState<string | null>(null);
    const inFlight = useRef(false);
    const echoing = awaitedSeq !== null && baseSeq < awaitedSeq;

    useEffect(() => {
        if (awaitedSeq !== null && baseSeq >= awaitedSeq) {
            setAwaitedSeq(null);
        }
    }, [awaitedSeq, baseSeq]);

    useEffect(() => {
        if (!echoing) {
            return;
        }
        const timer = window.setTimeout(() => {
            void onOutdated().finally(() => {
                setAwaitedSeq(null);
            });
        }, ECHO_TIMEOUT_MS);
        return (): void => {
            window.clearTimeout(timer);
        };
    }, [echoing, onOutdated]);

    const perform = useCallback(
        (call: (base: number) => Promise<number>, tolerated: string | null): void => {
            if (inFlight.current) {
                return;
            }
            inFlight.current = true;
            setSending(true);
            setNotice(null);
            setNoticeCode(null);
            void delivered(call, baseSeq, onOutdated)
                .then((accepted) => {
                    setAwaitedSeq(accepted);
                })
                .catch((trouble: unknown) => {
                    if (trouble instanceof Refused && trouble.code === tolerated) {
                        void onOutdated();
                        return;
                    }
                    if (trouble instanceof Refused && trouble.code === STALE_POSITION_CODE) {
                        void onOutdated();
                    }
                    setNotice(reasonOf(trouble));
                    setNoticeCode(trouble instanceof Refused ? trouble.code : UNKNOWN_CODE);
                })
                .finally(() => {
                    inFlight.current = false;
                    setSending(false);
                });
        },
        [baseSeq, onOutdated],
    );

    const send = useCallback(
        (move: Move, premove: boolean): void => {
            perform((base) => sendMove(seat, move, base, premove), null);
        },
        [seat, perform],
    );

    const revoke = useCallback((): void => {
        perform((base) => cancelPremove(seat, base), NO_PREMOVE_CODE);
    }, [seat, perform]);

    const clear = useCallback((): void => {
        setNotice(null);
        setNoticeCode(null);
    }, []);

    return { busy: sending || echoing, notice, noticeCode, send, revoke, clear };
}
