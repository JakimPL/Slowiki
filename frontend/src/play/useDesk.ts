import { useCallback, useEffect, useRef, useState } from "react";

import { sendMove } from "../api/client";
import { reorderMove } from "../api/moves";
import type { Seat } from "../api/seat";
import { reorderPayload } from "./arrangement";
import type { Desk, DeskEffect } from "./desk";
import { affected, EMPTY_DESK, reconciledDesk } from "./desk";
import { draftedIdentifiers } from "./draft";
import type { TableState } from "./events";

export interface DeskHold {
    readonly desk: Desk;
    readonly perform: (effect: DeskEffect) => void;
}

const REORDER_DELAY_MS = 800;

export function useDesk(state: TableState, mySeat: number | null, seat: Seat, active: boolean): DeskHold {
    const [desk, setDesk] = useState<Desk>(EMPTY_DESK);
    const rack = mySeat === null ? null : (state.view.racks[String(mySeat)] ?? null);
    const board = state.view.board;
    const seqRef = useRef(state.seq);

    useEffect(() => {
        seqRef.current = state.seq;
    }, [state.seq]);

    useEffect(() => {
        setDesk((current) => reconciledDesk(current, rack, board));
    }, [rack, board]);

    useEffect(() => {
        if (!active || mySeat === null || rack === null) {
            return;
        }
        const payload = reorderPayload(desk.arrangement, desk.tray, draftedIdentifiers(desk.draft));
        const served = rack.map((tile) => tile.identifier);
        const settled = payload.length === served.length && payload.every((id, at) => id === served[at]);
        if (settled) {
            return;
        }
        const timer = window.setTimeout(() => {
            void sendMove(seat, reorderMove(mySeat, payload), seqRef.current, false).catch(() => undefined);
        }, REORDER_DELAY_MS);
        return (): void => {
            window.clearTimeout(timer);
        };
    }, [desk.arrangement, desk.tray, desk.draft, rack, mySeat, seat, active]);

    const perform = useCallback((effect: DeskEffect): void => {
        setDesk((current) => affected(current, effect));
    }, []);

    return { desk, perform };
}
