import type { ReactElement } from "react";

export type StatusTone = "acting" | "quiet" | "over";

export interface StatusLineProps {
    readonly text: string;
    readonly tone: StatusTone;
}

export function StatusLine({ text, tone }: StatusLineProps): ReactElement {
    return (
        <p className="status-line" role="status" data-tone={tone}>
            {text}
        </p>
    );
}
