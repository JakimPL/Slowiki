import type { ReactElement } from "react";

import { STANDING_REOPEN } from "../strings";

export type StatusTone = "acting" | "quiet" | "over";

export interface StatusLineProps {
    readonly text: string;
    readonly tone: StatusTone;
    readonly onOpen: (() => void) | null;
}

export function StatusLine({ text, tone, onOpen }: StatusLineProps): ReactElement {
    if (onOpen === null) {
        return (
            <p className="status-line" role="status" data-tone={tone}>
                {text}
            </p>
        );
    }
    return (
        <button type="button" className="status-line" data-tone={tone} title={STANDING_REOPEN} onClick={onOpen}>
            {text}
        </button>
    );
}
