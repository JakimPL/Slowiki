import { useEffect, useRef, useState } from "react";

import { followEvents, readView } from "../api/client";
import { reasonOf } from "../api/refusal";
import type { Seat } from "../api/seat";
import type { Connection } from "./connection";
import type { TableState } from "./events";
import { accompanied, advanced, openedFrom } from "./events";
import { whileInView } from "./viewing";

export interface TableHold {
    readonly connection: Connection;
    readonly state: TableState | null;
    readonly trouble: string | null;
}

export function useTable(table: string, token: string | null): TableHold {
    const [connection, setConnection] = useState<Connection>("joining");
    const [state, setState] = useState<TableState | null>(null);
    const [trouble, setTrouble] = useState<string | null>(null);
    const sinceRef = useRef(0);

    useEffect(() => {
        let alive = true;
        let release: (() => void) | null = null;
        const seat: Seat = { table, token };
        readView(seat)
            .then((response) => {
                if (!alive) {
                    return;
                }
                sinceRef.current = response.seq;
                setState(openedFrom(response));
                release = whileInView(document, () =>
                    followEvents(seat, sinceRef.current, {
                        onOpen: (): void => {
                            setConnection("live");
                            setTrouble(null);
                        },
                        onCommit: (event): void => {
                            sinceRef.current = Math.max(sinceRef.current, event.seq + 1);
                            setState((current) => (current === null ? current : advanced(current, event)));
                        },
                        onPresence: (company): void => {
                            setState((current) => (current === null ? current : accompanied(current, company)));
                        },
                        onDropped: (reason): void => {
                            setConnection("resuming");
                            setTrouble(reason);
                        },
                    }),
                );
            })
            .catch((error: unknown) => {
                if (alive) {
                    setConnection("lost");
                    setTrouble(reasonOf(error));
                }
            });
        return (): void => {
            alive = false;
            if (release !== null) {
                release();
            }
        };
    }, [table, token]);

    return { connection, state, trouble };
}
