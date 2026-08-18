import type { ReactElement } from "react";

import { Invitation } from "../arrive/Invitation";
import { gatheringCaption } from "../strings";

export interface RoomProps {
    readonly table: string;
    readonly code: string | null;
    readonly present: number;
    readonly total: number;
}

export function Room({ table, code, present, total }: RoomProps): ReactElement {
    return (
        <section className="room">
            <p className="room-note">{gatheringCaption(present, total)}</p>
            {code !== null ? <Invitation table={table} code={code} /> : null}
        </section>
    );
}
