import type { ReactElement } from "react";

import type { LoreAnswer } from "../../play/lore/readings";
import { chosenReading } from "../../play/lore/readings";
import type { AskedWord } from "../../play/words/asked";
import { WORD_PANEL_CLOSE, WORD_VERDICT_CAPTIONS, wordPanelLabel, WORDS_HERE_LABEL } from "../strings";
import { WordParadigm } from "./WordParadigm";
import { WordReadings } from "./WordReadings";

export interface WordPanelProps {
    readonly asked: AskedWord;
    readonly words: readonly AskedWord[];
    readonly chosen: number;
    readonly answer: LoreAnswer;
    readonly lexeme: string | null;
    readonly onChoose: (chosen: number) => void;
    readonly onDeepen: (lexeme: string) => void;
    readonly onRetreat: () => void;
    readonly onClose: () => void;
}

export function WordPanel({
    asked,
    words,
    chosen,
    answer,
    lexeme,
    onChoose,
    onDeepen,
    onRetreat,
    onClose,
}: WordPanelProps): ReactElement {
    const verdict = WORD_VERDICT_CAPTIONS[asked.status];
    const reading = chosenReading(answer, lexeme);
    return (
        <div className="sheet-region">
            <button type="button" className="sheet-scrim" aria-label={WORD_PANEL_CLOSE} onClick={onClose} />
            <div
                className="sheet"
                data-depth={reading === null ? "card" : "paradigm"}
                role="dialog"
                aria-label={wordPanelLabel(asked.text)}
            >
                {reading === null && words.length > 1 ? (
                    <WordStrip words={words} chosen={chosen} onChoose={onChoose} />
                ) : null}
                <div className="word-head">
                    <h2 className="word-title">{asked.text}</h2>
                    {asked.points === null ? null : <span className="word-score">{asked.points}</span>}
                    {verdict === null ? null : (
                        <span className="word-verdict" data-status={asked.status}>
                            {verdict}
                        </span>
                    )}
                </div>
                {reading === null ? (
                    <WordReadings answer={answer} word={asked.text} onDeepen={onDeepen} />
                ) : (
                    <WordParadigm
                        readings={reading.readings}
                        reading={reading.reading}
                        word={asked.text}
                        onChoose={onDeepen}
                        onRetreat={onRetreat}
                    />
                )}
            </div>
        </div>
    );
}

interface WordStripProps {
    readonly words: readonly AskedWord[];
    readonly chosen: number;
    readonly onChoose: (chosen: number) => void;
}

function WordStrip({ words, chosen, onChoose }: WordStripProps): ReactElement {
    return (
        <ul className="word-strip" aria-label={WORDS_HERE_LABEL}>
            {words.map((word, index) => (
                <li key={`${word.text}-${String(index)}`}>
                    <button
                        type="button"
                        className="word-tab"
                        aria-pressed={index === chosen}
                        onClick={(): void => {
                            onChoose(index);
                        }}
                    >
                        {word.text}
                    </button>
                </li>
            ))}
        </ul>
    );
}
