import type { ReactElement } from "react";

import type { WordChip } from "../../play/words/chips";
import { bingoCaption, WORDS_LABEL } from "../strings";

export interface WordsProps {
    readonly chips: readonly WordChip[];
    readonly bingo: number;
    readonly openText: string | null;
    readonly onOpen: ((chip: WordChip) => void) | null;
}

export function Words({ chips, bingo, openText, onOpen }: WordsProps): ReactElement {
    return (
        <ul className="words" aria-label={WORDS_LABEL}>
            {chips.map((chip) => (
                <li key={chip.text} className="word-slot">
                    {onOpen === null ? (
                        <span className="word-chip" data-status={chip.status}>
                            <ChipFace chip={chip} />
                        </span>
                    ) : (
                        <button
                            type="button"
                            className="word-chip"
                            data-status={chip.status}
                            data-open={chip.text === openText ? "true" : undefined}
                            aria-haspopup="dialog"
                            aria-expanded={chip.text === openText}
                            onClick={(): void => {
                                onOpen(chip);
                            }}
                        >
                            <ChipFace chip={chip} />
                        </button>
                    )}
                </li>
            ))}
            {bingo > 0 ? (
                <li className="word-slot">
                    <span className="word-chip word-bingo" data-status="unknown">
                        {bingoCaption(bingo)}
                    </span>
                </li>
            ) : null}
        </ul>
    );
}

interface ChipFaceProps {
    readonly chip: WordChip;
}

function ChipFace({ chip }: ChipFaceProps): ReactElement {
    return (
        <>
            {chip.text}
            <b className="word-points">{chip.points}</b>
        </>
    );
}
