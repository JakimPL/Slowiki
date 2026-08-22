import type { ReactElement } from "react";

import { Invitation } from "../arrive/Invitation";
import { gatheringCaption } from "../strings";

export interface RoomProps {
    readonly code: string | null;
    readonly present: number;
    readonly total: number;
}

export function Room({ code, present, total }: RoomProps): ReactElement {
    return (
        <section className="room">
            <p className="room-note">{gatheringCaption(present, total)}</p>
            {code !== null ? <Invitation code={code} /> : null}
        </section>
    );
}
