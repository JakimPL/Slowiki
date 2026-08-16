import type { ReactElement } from "react";

import type { CompanyView, PositionView, SeatView } from "../api/views";
import { tintFor } from "../play/tints";
import { fallbackNameFor, OPEN_SEAT_LABEL, YOU_MARKER } from "./strings";

export interface PlaquesProps {
    readonly view: PositionView;
    readonly company: CompanyView;
    readonly mySeat: number | null;
}

export function Plaques({ view, company, mySeat }: PlaquesProps): ReactElement {
    return (
        <ul className="plaques">
            {company.seats.map((seated) => (
                <Plaque key={seated.seat} seated={seated} view={view} mine={seated.seat === mySeat} />
            ))}
        </ul>
    );
}

interface PlaqueProps {
    readonly seated: SeatView;
    readonly view: PositionView;
    readonly mine: boolean;
}

function Plaque({ seated, view, mine }: PlaqueProps): ReactElement {
    const acting = view.to_act.includes(seated.seat);
    const premoved = view.pending_premoves.includes(seated.seat);
    const score = view.scores[String(seated.seat)] ?? 0;
    return (
        <li
            className="plaque"
            data-acting={acting ? "true" : undefined}
            data-open={seated.claimed ? undefined : "true"}
            data-connected={seated.connected ? "true" : undefined}
            style={{ "--tint": tintFor(seated.seat).hex }}
        >
            <i className="plaque-dot" aria-hidden="true" />
            <span className="plaque-name">
                {seated.claimed ? (seated.name ?? fallbackNameFor(seated.seat)) : OPEN_SEAT_LABEL}
            </span>
            {mine ? <em className="plaque-you">{YOU_MARKER}</em> : null}
            {premoved ? <i className="plaque-premove" aria-hidden="true" /> : null}
            <span className="plaque-score">{score}</span>
        </li>
    );
}
