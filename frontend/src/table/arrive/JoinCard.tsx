import type { ReactElement, SubmitEventHandler } from "react";

import type { OfferingsResponse } from "../../api/tables";
import { outsideGroup } from "../../play/rules/deviation";
import type { Inspecting } from "../../play/rules/inspecting";
import { inspecting } from "../../play/rules/inspecting";
import type { Invited } from "../../play/rules/useInvitation";
import { useInvitation } from "../../play/rules/useInvitation";
import { enteredCode } from "../../play/seats/codes";
import {
    CODE_HINT,
    CODE_LABEL,
    JOIN_BUTTON,
    JOIN_HEADING,
    READING_TABLE,
    rulesCaption,
    standingCaption,
} from "../strings";

const CARD_GROUP = "table";

export interface JoinCardProps {
    readonly code: string;
    readonly arrivals: OfferingsResponse | null;
    readonly busy: boolean;
    readonly named: boolean;
    readonly onCode: (code: string) => void;
    readonly onJoin: () => void;
    readonly onInspect: (inspected: Inspecting) => void;
}

export function JoinCard({ code, arrivals, busy, named, onCode, onJoin, onInspect }: JoinCardProps): ReactElement {
    const shape = arrivals?.code ?? null;
    const complete = shape === null ? code.trim() !== "" : code.length === shape.length;
    const invited = useInvitation(code, shape);
    const reading = inspecting(arrivals, invited.description);
    const submit: SubmitEventHandler<HTMLFormElement> = (submission) => {
        submission.preventDefault();
        if (complete && named) {
            onJoin();
        }
    };
    return (
        <form className="panel" onSubmit={submit}>
            <h2>{JOIN_HEADING}</h2>
            <label className="field">
                <span>{CODE_LABEL}</span>
                <input
                    type="text"
                    className="code-input"
                    value={code}
                    autoCapitalize="characters"
                    inputMode="text"
                    onChange={(change): void => {
                        onCode(
                            shape === null
                                ? change.target.value.toUpperCase()
                                : enteredCode(change.target.value, shape),
                        );
                    }}
                />
            </label>
            <div className="join-slot">
                <p className="join-line">{firstLine(invited, reading)}</p>
                {reading === null ? (
                    <p className="join-line" />
                ) : (
                    <button
                        type="button"
                        className="join-rules"
                        onClick={(): void => {
                            onInspect(reading);
                        }}
                    >
                        {rulesCaption(outsideGroup(reading.deviations, CARD_GROUP).length)}
                    </button>
                )}
            </div>
            <button type="submit" className="action" disabled={busy || !named || !complete}>
                {JOIN_BUTTON}
            </button>
        </form>
    );
}

function firstLine(invited: Invited, reading: Inspecting | null): string {
    if (invited.refused !== null) {
        return invited.refused;
    }
    if (reading !== null && reading.record !== null) {
        return standingCaption(reading.scheme, reading.record);
    }
    if (invited.reading) {
        return READING_TABLE;
    }
    return CODE_HINT;
}
