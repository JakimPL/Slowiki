import { useCallback, useEffect, useState } from "react";

import type { Seat } from "../../api/seat";
import type { TableAdmission } from "../../api/tables";
import { forgetSeat, rememberSeat, storedSeat } from "./memory";
import { followedFragment, fragmentFor, standingIn, withoutFragment } from "./session";

export interface Arrival {
    readonly seat: Seat;
    readonly code: string | null;
    readonly seated: number | null;
}

export interface StandingHold {
    readonly arrival: Arrival | null;
    readonly invitation: string | null;
    readonly arrive: (admission: TableAdmission) => void;
    readonly leave: () => void;
    readonly resume: (() => void) | null;
    readonly forget: () => void;
}

export function useStanding(): StandingHold {
    const [fragment, setFragment] = useState(() => window.location.hash);
    const [remembered, setRemembered] = useState(() => storedSeat(window.sessionStorage));
    const reach = useCallback((reached: string): void => {
        window.history.replaceState(null, "", reached === "" ? withoutFragment(window.location.href) : reached);
        setFragment(reached);
    }, []);
    const arrive = useCallback(
        (admission: TableAdmission): void => {
            reach(fragmentFor(admission.table_id, admission.token, admission.code, admission.seat));
        },
        [reach],
    );
    const leave = useCallback((): void => {
        reach("");
    }, [reach]);
    const resume = useCallback((): void => {
        if (remembered !== null) {
            reach(remembered);
        }
    }, [reach, remembered]);
    const forget = useCallback((): void => {
        forgetSeat(window.sessionStorage);
        setRemembered(null);
    }, []);

    const standing = standingIn(fragment);
    const arrival =
        standing.table !== null && standing.token !== null
            ? { seat: { table: standing.table, token: standing.token }, code: standing.code, seated: standing.seated }
            : null;
    const seated = arrival === null ? null : fragment;

    useEffect(() => {
        if (seated !== null) {
            rememberSeat(seated, window.sessionStorage);
            setRemembered(seated);
        }
    }, [seated]);

    useEffect(() => {
        const reread = (): void => {
            const followed = followedFragment(fragment, window.location.hash);
            if (followed !== window.location.hash) {
                window.history.replaceState(null, "", followed);
            }
            setFragment(followed);
        };
        window.addEventListener("hashchange", reread);
        return (): void => {
            window.removeEventListener("hashchange", reread);
        };
    }, [fragment]);

    return {
        arrival,
        invitation: arrival === null ? standing.code : null,
        arrive,
        leave,
        resume: remembered === null ? null : resume,
        forget,
    };
}
