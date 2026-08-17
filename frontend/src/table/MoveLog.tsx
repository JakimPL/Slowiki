import type { CSSProperties, ReactElement } from "react";

import type { CompanyView } from "../api/views";
import type { LogEntry } from "../play/log";
import { tintFor } from "../play/tints";
import { DOCKET_GROUP, LOG_LABEL, logCaption, nameFor } from "./strings";

export interface MoveLogProps {
    readonly log: readonly LogEntry[];
    readonly company: CompanyView;
}

export function MoveLog({ log, company }: MoveLogProps): ReactElement {
    const newestFirst = [...log].reverse();
    const latest = newestFirst[0] ?? null;
    return (
        <details className="log" name={DOCKET_GROUP}>
            <summary>
                {latest === null ? (
                    LOG_LABEL
                ) : (
                    <>
                        <i className="move-log-dot" aria-hidden="true" style={tinted(latest.actor)} />
                        <span className="log-latest">
                            {nameFor(company, latest.actor)} · {logCaption(latest)}
                        </span>
                    </>
                )}
            </summary>
            <ol className="log-list" aria-label={LOG_LABEL}>
                {newestFirst.map((entry) => (
                    <li key={entry.seq} className="move-log-entry" data-kind={entry.kind} style={tinted(entry.actor)}>
                        <i className="move-log-dot" aria-hidden="true" />
                        <span className="move-log-name">{nameFor(company, entry.actor)}</span>
                        <span className="move-log-what">{logCaption(entry)}</span>
                    </li>
                ))}
            </ol>
        </details>
    );
}

function tinted(actor: number): CSSProperties {
    return { "--tint": tintFor(actor).hex };
}
