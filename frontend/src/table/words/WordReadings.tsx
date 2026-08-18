import type { ReactElement } from "react";

import type { LoreReading } from "../../api/lore";
import { inflectionTerms } from "../../play/lore/inflection";
import type { LoreAnswer } from "../../play/lore/readings";
import { askedFormsOf, loreStateOf } from "../../play/lore/readings";
import type { Dimension } from "../../play/lore/tagset";
import {
    baseCaption,
    odmianaCaption,
    WORD_ABSENT_NOTE,
    WORD_ASKING_NOTE,
    WORD_FAILED_NOTE,
    WORD_SAMPLE_NOTE,
    WORD_UNCLASSIFIED_NOTE,
    WORD_UNCLASSIFIED_PART,
} from "../strings";

const NO_DIMENSIONS: readonly Dimension[] = [];

export interface WordReadingsProps {
    readonly answer: LoreAnswer;
    readonly word: string;
}

export function WordReadings({ answer, word }: WordReadingsProps): ReactElement {
    if (answer.state === "asking") {
        return <p className="word-note">{WORD_ASKING_NOTE}</p>;
    }
    if (answer.state === "failed" || answer.lore === null) {
        return <p className="word-note">{WORD_FAILED_NOTE}</p>;
    }
    const state = loreStateOf(answer.lore);
    if (state === "absent") {
        return <p className="word-note">{WORD_ABSENT_NOTE}</p>;
    }
    return (
        <div className="word-readings">
            {state === "unclassified" ? (
                <Unclassified />
            ) : (
                answer.lore.readings.map((reading) => <Reading key={reading.lexeme} reading={reading} word={word} />)
            )}
            {answer.sample ? <p className="word-sample">{WORD_SAMPLE_NOTE}</p> : null}
        </div>
    );
}

interface ReadingProps {
    readonly reading: LoreReading;
    readonly word: string;
}

function Reading({ reading, word }: ReadingProps): ReactElement {
    const asked = askedFormsOf(reading, word);
    const lines = [...new Set(asked.map((form) => odmianaCaption(inflectionTerms(form.tags, NO_DIMENSIONS))))];
    return (
        <div className="word-reading">
            <span className="word-lemma">
                <span className="word-part">{reading.part}</span>
                {baseCaption(reading.base)}
            </span>
            {lines.map((line) => (
                <span key={line} className="word-odmiana">
                    {line}
                </span>
            ))}
        </div>
    );
}

function Unclassified(): ReactElement {
    return (
        <div className="word-reading" data-quiet="true">
            <span className="word-lemma">
                <span className="word-part">{WORD_UNCLASSIFIED_PART}</span>
            </span>
            <span className="word-odmiana">{WORD_UNCLASSIFIED_NOTE}</span>
        </div>
    );
}
