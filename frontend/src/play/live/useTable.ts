import { useCallback, useEffect, useRef, useState } from "react";

import { followEvents, readView } from "../../api/client";
import { reasonOf } from "../../api/refusal";
import type { Seat } from "../../api/seat";
import type { ClockView } from "../../api/views";
import { whenInView } from "../device/viewing";
import type { Connection } from "./connection";
import type { TableState } from "./events";
import { accompanied, advanced, openedFrom, positioned, refreshed } from "./events";
import { silent, WATCH_INTERVAL_MILLISECONDS } from "./liveness";

export interface TableHold {
    readonly connection: Connection;
    readonly state: TableState | null;
    readonly clock: ClockView | null;
    readonly trouble: string | null;
    readonly refresh: () => Promise<number | null>;
}

export function useTable(table: string, token: string | null): TableHold {
    const [connection, setConnection] = useState<Connection>("joining");
    const [state, setState] = useState<TableState | null>(null);
    const [clock, setClock] = useState<ClockView | null>(null);
    const [trouble, setTrouble] = useState<string | null>(null);
    const sinceRef = useRef(0);
    const refreshRef = useRef<() => Promise<number | null>>(() => Promise.resolve(null));

    useEffect(() => {
        let alive = true;
        let release: (() => void) | null = null;
        let lastBeat = Date.now();
        const seat: Seat = { table, token };
        const refresh = (): Promise<number | null> =>
            readView(seat)
                .then((response) => {
                    if (!alive) {
                        return null;
                    }
                    sinceRef.current = Math.max(sinceRef.current, response.seq);
                    setClock(response.clock);
                    setState((current) => (current === null ? openedFrom(response) : refreshed(current, response)));
                    return response.seq;
                })
                .catch((error: unknown) => {
                    if (alive) {
                        setTrouble(reasonOf(error));
                    }
                    return null;
                });
        refreshRef.current = refresh;

        const hold = (): (() => void) => {
            lastBeat = Date.now();
            return followEvents(seat, sinceRef.current, {
                onOpen: (): void => {
                    setConnection("live");
                    setTrouble(null);
                },
                onBeat: (): void => {
                    lastBeat = Date.now();
                },
                onCommit: (event): void => {
                    sinceRef.current = Math.max(sinceRef.current, event.seq + 1);
                    setState((current) => (current === null ? current : advanced(current, event)));
                },
                onPresence: (company): void => {
                    setState((current) => (current === null ? current : accompanied(current, company)));
                },
                onPosition: (view): void => {
                    setState((current) => (current === null ? current : positioned(current, view)));
                },
                onClock: (served): void => {
                    setClock(served);
                },
                onDropped: (reason): void => {
                    setConnection("resuming");
                    setTrouble(reason);
                },
            });
        };

        const resume = (): void => {
            if (!alive) {
                return;
            }
            setConnection("resuming");
            if (release !== null) {
                release();
            }
            void refresh();
            release = hold();
        };

        readView(seat)
            .then((response) => {
                if (!alive) {
                    return;
                }
                sinceRef.current = response.seq;
                setClock(response.clock);
                setState(openedFrom(response));
                release = hold();
            })
            .catch((error: unknown) => {
                if (alive) {
                    setConnection("lost");
                    setTrouble(reasonOf(error));
                }
            });

        const resumedIfSilent = (): boolean => {
            if (!silent(lastBeat, Date.now())) {
                return false;
            }
            resume();
            return true;
        };

        const watchdog = window.setInterval((): void => {
            resumedIfSilent();
        }, WATCH_INTERVAL_MILLISECONDS);
        const stopWatchingView = whenInView(document, (): void => {
            if (!resumedIfSilent()) {
                void refresh();
            }
        });

        return (): void => {
            alive = false;
            window.clearInterval(watchdog);
            stopWatchingView();
            if (release !== null) {
                release();
            }
        };
    }, [table, token]);

    const refresh = useCallback((): Promise<number | null> => refreshRef.current(), []);

    return { connection, state, clock, trouble, refresh };
}
