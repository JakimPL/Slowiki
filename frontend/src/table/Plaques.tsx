import type { ReactElement } from "react";

import type { CompanyView, PositionView, SeatView } from "../api/views";
import type { Urgency } from "../play/clock";
import { tintFor } from "../play/tints";
import { fallbackNameFor, OPEN_SEAT_LABEL, PLAYERS_LABEL, YOU_MARKER } from "./strings";

export interface SeatCountdown {
    readonly seat: number;
    readonly caption: string;
    readonly urgency: Urgency;
}

export interface PlaquesProps {
    readonly view: PositionView;
    readonly company: CompanyView;
    readonly mySeat: number | null;
    readonly countdown: SeatCountdown | null;
}

export function Plaques({ view, company, mySeat, countdown }: PlaquesProps): ReactElement {
    return (
        <ul className="plaques" aria-label={PLAYERS_LABEL}>
            {company.seats.map((seated) => (
                <Plaque
                    key={seated.seat}
                    seated={seated}
                    view={view}
                    mine={seated.seat === mySeat}
                    countdown={countdown?.seat === seated.seat ? countdown : null}
                />
            ))}
        </ul>
    );
}

interface PlaqueProps {
    readonly seated: SeatView;
    readonly view: PositionView;
    readonly mine: boolean;
    readonly countdown: SeatCountdown | null;
}

function Plaque({ seated, view, mine, countdown }: PlaqueProps): ReactElement {
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
            <span className="plaque-name">
                <i className="plaque-dot" aria-hidden="true" />
                <span className="plaque-name-text">
                    {seated.claimed ? (seated.name ?? fallbackNameFor(seated.seat)) : OPEN_SEAT_LABEL}
                </span>
                {mine ? <em className="plaque-you">{YOU_MARKER}</em> : null}
                {premoved ? <i className="plaque-premove" aria-hidden="true" /> : null}
            </span>
            <span className="plaque-score">
                {score}
                {countdown === null ? null : (
                    <span className="plaque-clock" data-urgency={countdown.urgency}>
                        {countdown.caption}
                    </span>
                )}
            </span>
        </li>
    );
}
