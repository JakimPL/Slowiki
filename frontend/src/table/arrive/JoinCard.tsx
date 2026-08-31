import type { ReactElement, SubmitEventHandler } from "react";

import type { CodeShape } from "../../play/seats/codes";
import { enteredCode } from "../../play/seats/codes";
import { CODE_LABEL, JOIN_BUTTON, JOIN_HEADING } from "../strings";

export interface JoinCardProps {
    readonly code: string;
    readonly shape: CodeShape | null;
    readonly busy: boolean;
    readonly named: boolean;
    readonly onCode: (code: string) => void;
    readonly onJoin: () => void;
}

export function JoinCard({ code, shape, busy, named, onCode, onJoin }: JoinCardProps): ReactElement {
    const complete = shape === null ? code.trim() !== "" : code.length === shape.length;
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
            <button type="submit" className="action" disabled={busy || !named || !complete}>
                {JOIN_BUTTON}
            </button>
        </form>
    );
}
