import type { CSSProperties, ReactElement } from "react";
import { Fragment } from "react";

import type { CompanyView } from "../../api/views";
import type { ScoredWord } from "../../play/board/scoring";
import { tintFor } from "../../play/seats/tints";
import type { LogEntry } from "../../play/story/log";
import {
    DOCKET_GROUP,
    LIST_SEPARATOR,
    LOG_LABEL,
    logCaption,
    logScoreCaption,
    nameFor,
    openWordLabel,
} from "../strings";

export interface MoveLogProps {
    readonly log: readonly LogEntry[];
    readonly company: CompanyView;
    readonly onOpen: ((word: ScoredWord) => void) | null;
}

export function MoveLog({ log, company, onOpen }: MoveLogProps): ReactElement {
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
                        <span className="move-log-what">
                            {entry.kind === "play" && onOpen !== null ? (
                                <PlayedWords entry={entry} onOpen={onOpen} />
                            ) : (
                                logCaption(entry)
                            )}
                        </span>
                    </li>
                ))}
            </ol>
        </details>
    );
}

interface PlayedWordsProps {
    readonly entry: LogEntry;
    readonly onOpen: (word: ScoredWord) => void;
}

function PlayedWords({ entry, onOpen }: PlayedWordsProps): ReactElement {
    return (
        <>
            {entry.words.map((word, index) => (
                <Fragment key={`${word.text}-${String(index)}`}>
                    {index > 0 ? LIST_SEPARATOR : null}
                    <button
                        type="button"
                        className="log-word"
                        aria-haspopup="dialog"
                        aria-label={openWordLabel(word.text)}
                        onClick={(): void => {
                            onOpen(word);
                        }}
                    >
                        {word.text}
                    </button>
                </Fragment>
            ))}
            {logScoreCaption(entry.points ?? 0)}
        </>
    );
}

function tinted(actor: number): CSSProperties {
    return { "--tint": tintFor(actor).hex };
}
