import type { CSSProperties, ReactElement } from "react";

import type { CompanyView } from "../api/views";
import type { LogEntry } from "../play/log";
import { tintFor } from "../play/tints";
import { LOG_LABEL, logCaption, nameFor } from "./strings";

export interface MoveLogProps {
    readonly log: readonly LogEntry[];
    readonly company: CompanyView;
}

export function MoveLog({ log, company }: MoveLogProps): ReactElement {
    const newestFirst = [...log].reverse();
    return (
        <ol className="move-log" aria-label={LOG_LABEL}>
            {newestFirst.map((entry) => {
                const style: CSSProperties = { "--tint": tintFor(entry.actor).hex };
                return (
                    <li key={entry.seq} className="move-log-entry" data-kind={entry.kind} style={style}>
                        <i className="move-log-dot" aria-hidden="true" />
                        <span className="move-log-name">{nameFor(company, entry.actor)}</span>
                        <span className="move-log-what">{logCaption(entry)}</span>
                    </li>
                );
            })}
        </ol>
    );
}
