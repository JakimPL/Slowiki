import type { CSSProperties, ReactElement } from "react";
import { useState } from "react";

import { readWordAnalyses } from "../api/client";
import type { CompanyView, Schemas } from "../api/views";
import type { LogEntry } from "../play/log";
import { tintFor } from "../play/tints";
import { LOG_LABEL, logCaption, nameFor, WORD_CLASS_EMPTY_LABEL } from "./strings";

export interface MoveLogProps {
    readonly log: readonly LogEntry[];
    readonly company: CompanyView;
    readonly tableId: string | null;
}

interface WordInspection {
    readonly word: string;
    readonly analyses: Schemas["WordAnalyses"];
}

export function MoveLog({ log, company, tableId }: MoveLogProps): ReactElement {
    const newestFirst = [...log].reverse();
    const latest = newestFirst[0] ?? null;
    const [inspection, setInspection] = useState<WordInspection | null>(null);

    const inspect = async (word: string): Promise<void> => {
        if (tableId === null) {
            return;
        }
        setInspection({ word, analyses: await readWordAnalyses(tableId, word) });
    };

    return (
        <details className="log">
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
                        {entry.kind === "play" && (
                            <span className="move-log-words">
                                {entry.words.map((word) => (
                                    <button
                                        key={word.text}
                                        className="word-chip"
                                        disabled={tableId === null}
                                        onClick={(): void => {
                                            void inspect(word.text);
                                        }}
                                    >
                                        {word.text}
                                    </button>
                                ))}
                            </span>
                        )}
                    </li>
                ))}
            </ol>
            {inspection !== null && (
                <div className="word-analysis" role="status">
                    <span className="word-analysis-word">{inspection.word}</span>
                    {inspection.analyses.analyses.length === 0 ? (
                        <span className="word-analysis-empty">{WORD_CLASS_EMPTY_LABEL}</span>
                    ) : (
                        <ul>
                            {inspection.analyses.analyses.map((analysis, index) => (
                                <li key={index} className="word-analysis-entry">
                                    {analysis.part} · {analysis.lemma}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </details>
    );
}

function tinted(actor: number): CSSProperties {
    return { "--tint": tintFor(actor).hex };
}
