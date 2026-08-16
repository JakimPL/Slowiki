import { useCallback, useState } from "react";

import type { Seat } from "../api/seat";
import type { TableAdmission } from "../api/tables";
import { fragmentFor, standingIn } from "./session";

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
    const [standing, setStanding] = useState(() => standingIn(window.location.hash));
    const arrive = useCallback((admission: TableAdmission): void => {
        const fragment = fragmentFor(admission.table_id, admission.token, admission.code, admission.seat);
        window.history.replaceState(null, "", fragment);
        setStanding(standingIn(fragment));
    }, []);
    const arrival =
        standing.table !== null && standing.token !== null
            ? { seat: { table: standing.table, token: standing.token }, code: standing.code, seated: standing.seated }
            : null;
    return { arrival, invitation: arrival === null ? standing.code : null, arrive };
}
