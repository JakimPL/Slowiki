import { useCallback, useState } from "react";

import type { PlayRecord } from "../../api/views";
import type { FreshFrame, FreshMark } from "./fresh";
import { BEFORE_ANY_TURN, freshFrame, freshMarks } from "./fresh";

export interface FreshHold {
    readonly marks: ReadonlyMap<number, FreshMark>;
    readonly frame: FreshFrame | null;
    readonly acknowledge: () => void;
}

export function useFreshPlay(play: PlayRecord | null, mySeat: number | null, size: number): FreshHold {
    const [acknowledged, setAcknowledged] = useState(BEFORE_ANY_TURN);
    const turn = play?.turn_number ?? BEFORE_ANY_TURN;
    const acknowledge = useCallback((): void => {
        setAcknowledged((seen) => Math.max(seen, turn));
    }, [turn]);
    return { marks: freshMarks(play, mySeat, acknowledged), frame: freshFrame(play, size), acknowledge };
}
