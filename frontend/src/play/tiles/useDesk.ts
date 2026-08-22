import { useCallback, useEffect, useMemo, useState } from "react";

import { sendRackOrder } from "../../api/client";
import type { Seat } from "../../api/seat";
import type { TableState } from "../live/events";
import { rackOrder } from "./arrangement";
import type { Desk, DeskEffect } from "./desk";
import { affected, EMPTY_DESK, reconciledDesk } from "./desk";
import { draftedIdentifiers } from "./draft";
import { NO_COMMITTED_TILES, queuedPremoveOf } from "./premoves";

export interface DeskHold {
    readonly desk: Desk;
    readonly perform: (effect: DeskEffect) => void;
}

const RACK_ORDER_DELAY_MS = 800;

export function useDesk(state: TableState, mySeat: number | null, seat: Seat, active: boolean): DeskHold {
    const [desk, setDesk] = useState<Desk>(EMPTY_DESK);
    const rack = mySeat === null ? null : (state.view.racks[String(mySeat)] ?? null);
    const board = state.view.board;
    const committed = useMemo(
        () => queuedPremoveOf(state.view, mySeat)?.committed ?? NO_COMMITTED_TILES,
        [state.view, mySeat],
    );

    useEffect(() => {
        setDesk((current) => reconciledDesk(current, rack, board, committed));
    }, [rack, board, committed]);

    useEffect(() => {
        if (!active || rack === null) {
            return;
        }
        const asked = rackOrder(desk.arrangement, desk.tray, draftedIdentifiers(desk.draft));
        const served = rack.map((tile) => tile.identifier);
        const settled = asked.length === served.length && asked.every((id, at) => id === served[at]);
        if (settled) {
            return;
        }
        const timer = window.setTimeout(() => {
            void sendRackOrder(seat, asked).catch(() => undefined);
        }, RACK_ORDER_DELAY_MS);
        return (): void => {
            window.clearTimeout(timer);
        };
    }, [desk.arrangement, desk.tray, desk.draft, rack, seat, active]);

    const perform = useCallback((effect: DeskEffect): void => {
        setDesk((current) => affected(current, effect));
    }, []);

    return { desk, perform };
}
