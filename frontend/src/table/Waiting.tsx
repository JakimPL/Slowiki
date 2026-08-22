import type { ReactElement } from "react";

import { TABLE_LEAVE } from "./strings";

export interface WaitingProps {
    readonly note: string;
    readonly onLeave: (() => void) | null;
}

export function Waiting({ note, onLeave }: WaitingProps): ReactElement {
    return (
        <main className="waiting">
            <p role="status">{note}</p>
            {onLeave === null ? null : (
                <button type="button" className="action action-quiet" onClick={onLeave}>
                    {TABLE_LEAVE}
                </button>
            )}
        </main>
    );
}
