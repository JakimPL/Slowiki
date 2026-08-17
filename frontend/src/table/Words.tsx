import type { ReactElement } from "react";

import type { WordStatus } from "../play/feedback";
import { bingoCaption, WORDS_LABEL } from "./strings";

export interface WordChip {
    readonly text: string;
    readonly points: number;
    readonly status: WordStatus;
}

export interface WordsProps {
    readonly chips: readonly WordChip[];
    readonly bingo: number;
}

export function Words({ chips, bingo }: WordsProps): ReactElement {
    return (
        <ul className="words" aria-label={WORDS_LABEL}>
            {chips.map((chip) => (
                <li key={chip.text} className="word-chip" data-status={chip.status}>
                    {chip.text}
                    <b className="word-points">{chip.points}</b>
                </li>
            ))}
            {bingo > 0 ? (
                <li className="word-chip word-bingo" data-status="unknown">
                    {bingoCaption(bingo)}
                </li>
            ) : null}
        </ul>
    );
}
