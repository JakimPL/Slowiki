import { useCallback, useEffect, useState } from "react";

import type { PositionView } from "../api/views";
import type { Desk, DeskEffect } from "./desk";
import { affected, EMPTY_DESK, reconciledDesk } from "./desk";

export interface DeskHold {
    readonly desk: Desk;
    readonly perform: (effect: DeskEffect) => void;
}

export function useDesk(view: PositionView, mySeat: number | null): DeskHold {
    const [desk, setDesk] = useState<Desk>(EMPTY_DESK);
    const rack = mySeat === null ? null : (view.racks[String(mySeat)] ?? null);
    const board = view.board;

    useEffect(() => {
        setDesk((current) => reconciledDesk(current, rack, board));
    }, [rack, board]);

    const perform = useCallback((effect: DeskEffect): void => {
        setDesk((current) => affected(current, effect));
    }, []);

    return { desk, perform };
}
