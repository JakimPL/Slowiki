import type { ReactElement } from "react";

import type { LoreAnswer } from "../../play/lore/readings";
import { chosenReading } from "../../play/lore/readings";
import type { WordChip } from "../../play/words/chips";
import { WORD_PANEL_CLOSE, WORD_VERDICT_CAPTIONS, wordPanelLabel } from "../strings";
import { WordParadigm } from "./WordParadigm";
import { WordReadings } from "./WordReadings";

export interface WordPanelProps {
    readonly chip: WordChip;
    readonly answer: LoreAnswer;
    readonly lexeme: string | null;
    readonly onDeepen: (lexeme: string) => void;
    readonly onRetreat: () => void;
    readonly onClose: () => void;
}

export function WordPanel({ chip, answer, lexeme, onDeepen, onRetreat, onClose }: WordPanelProps): ReactElement {
    const verdict = WORD_VERDICT_CAPTIONS[chip.status];
    const chosen = chosenReading(answer, lexeme);
    return (
        <div className="sheet-region">
            <button type="button" className="sheet-scrim" aria-label={WORD_PANEL_CLOSE} onClick={onClose} />
            <div
                className="sheet"
                data-depth={chosen === null ? "card" : "paradigm"}
                role="dialog"
                aria-label={wordPanelLabel(chip.text)}
            >
                <div className="word-head">
                    <h2 className="word-title">{chip.text}</h2>
                    <span className="word-score">{chip.points}</span>
                    {verdict === null ? null : (
                        <span className="word-verdict" data-status={chip.status}>
                            {verdict}
                        </span>
                    )}
                </div>
                {chosen === null ? (
                    <WordReadings answer={answer} word={chip.text} onDeepen={onDeepen} />
                ) : (
                    <WordParadigm
                        readings={chosen.readings}
                        reading={chosen.reading}
                        word={chip.text}
                        onChoose={onDeepen}
                        onRetreat={onRetreat}
                    />
                )}
            </div>
        </div>
    );
}
