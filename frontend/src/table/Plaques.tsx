import type { ReactElement } from "react";

import type { CompanyView, PositionView, SeatView } from "../api/views";
import type { Urgency } from "../play/clock";
import { tintFor } from "../play/tints";
import { EMPTY_CLOCK, fallbackNameFor, OPEN_SEAT_LABEL, PLAYERS_LABEL, YOU_MARKER } from "./strings";

export interface SeatClock {
    readonly caption: string;
    readonly urgency: Urgency;
}

export interface PlaquesProps {
    readonly view: PositionView;
    readonly company: CompanyView;
    readonly mySeat: number | null;
    readonly clocks: ReadonlyMap<number, SeatClock>;
    readonly clocked: boolean;
}

export function Plaques({ view, company, mySeat, clocks, clocked }: PlaquesProps): ReactElement {
    return (
        <ul className="plaques" aria-label={PLAYERS_LABEL}>
            {company.seats.map((seated) => (
                <Plaque
                    key={seated.seat}
                    seated={seated}
                    view={view}
                    mine={seated.seat === mySeat}
                    countdown={clocks.get(seated.seat) ?? null}
                    clocked={clocked}
                />
            ))}
        </ul>
    );
}

interface PlaqueProps {
    readonly seated: SeatView;
    readonly view: PositionView;
    readonly mine: boolean;
    readonly countdown: SeatClock | null;
    readonly clocked: boolean;
}

function Plaque({ seated, view, mine, countdown, clocked }: PlaqueProps): ReactElement {
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
            <span className="plaque-score">{score}</span>
            {clocked ? (
                <span className="plaque-clock" data-urgency={countdown?.urgency}>
                    {countdown?.caption ?? EMPTY_CLOCK}
                </span>
            ) : null}
        </li>
    );
}
