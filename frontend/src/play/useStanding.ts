import { useCallback, useEffect, useState } from "react";

import type { Seat } from "../api/seat";
import type { TableAdmission } from "../api/tables";
import { followedFragment, fragmentFor, standingIn } from "./session";

export interface Arrival {
    readonly seat: Seat;
    readonly code: string | null;
    readonly seated: number | null;
}

export interface StandingHold {
    readonly arrival: Arrival | null;
    readonly invitation: string | null;
    readonly arrive: (admission: TableAdmission) => void;
}

export function useStanding(): StandingHold {
    const [fragment, setFragment] = useState(() => window.location.hash);
    const arrive = useCallback((admission: TableAdmission): void => {
        const reached = fragmentFor(admission.table_id, admission.token, admission.code, admission.seat);
        window.history.replaceState(null, "", reached);
        setFragment(reached);
    }, []);

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

    const standing = standingIn(fragment);
    const arrival =
        standing.table !== null && standing.token !== null
            ? { seat: { table: standing.table, token: standing.token }, code: standing.code, seated: standing.seated }
            : null;
    return { arrival, invitation: arrival === null ? standing.code : null, arrive };
}
