import type { ReactElement } from "react";
import { useState } from "react";

import type { AlphabetPreset, DistributionPreset } from "../../api/tables";
import type { Tile } from "../../api/views";
import type { LetterChange } from "../../play/rules/adjustments";
import { withCategory, withLetter } from "../../play/rules/adjustments";
import type { LetterRow } from "../../play/rules/letters";
import { bagTotal, categoriesOf, letterRows } from "../../play/rules/letters";
import type { Composing } from "../../play/rules/useComposing";
import {
    bagTotalCaption,
    categoryCaption,
    LETTER_BULK_LABEL,
    LETTER_CATEGORY,
    LETTER_COUNT,
    LETTER_POINTS,
} from "../strings";
import { TileFace } from "../tiles/TileFace";
import { Picker } from "./Picker";
import { Stepper } from "./Stepper";

const NO_IDENTIFIER = 0;

export interface LettersEditorProps {
    readonly composing: Composing;
    readonly alphabet: AlphabetPreset;
    readonly distribution: DistributionPreset;
    readonly minimum: number;
    readonly maximum: number;
    readonly step: number;
    readonly readOnly: boolean;
}

export function LettersEditor({
    composing,
    alphabet,
    distribution,
    minimum,
    maximum,
    step,
    readOnly,
}: LettersEditorProps): ReactElement {
    const record = composing.record;
    const adjustments = record?.letters ?? {};
    const standard = letterRows(alphabet, distribution, {});
    const rows = letterRows(alphabet, distribution, adjustments);
    const categories = categoriesOf(standard);
    const [held, setHeld] = useState(rows[0]?.symbol ?? "");
    const [colored, setColored] = useState(categories[0] ?? "");
    const chosen = rows.find((row) => row.symbol === held) ?? rows[0] ?? null;
    const coloredOptions = categories.map((category) => ({ value: category, caption: categoryCaption(category) }));
    const change = (symbol: string, asked: LetterChange): void => {
        composing.setSetting("letters", withLetter(adjustments, standard, symbol, asked));
    };
    return (
        <>
            {categories.length > 1 ? (
                <div className="menu-row">
                    <span className="menu-label">{LETTER_BULK_LABEL}</span>
                    <Picker
                        label={LETTER_CATEGORY}
                        value={colored}
                        options={coloredOptions}
                        readOnly={readOnly}
                        onChange={setColored}
                    />
                    <Stepper
                        label={LETTER_BULK_LABEL}
                        value={pointsOf(rows, colored)}
                        minimum={minimum}
                        maximum={maximum}
                        step={step}
                        disabled={readOnly}
                        onChange={(value): void => {
                            composing.setSetting("letters", withCategory(adjustments, standard, colored, value));
                        }}
                    />
                </div>
            ) : null}
            <div className="letters-grid">
                {rows.map((row) => (
                    <button
                        key={row.symbol}
                        type="button"
                        className="letters-cell"
                        aria-pressed={row.symbol === chosen?.symbol}
                        data-changed={row.changed ? "true" : undefined}
                        onClick={(): void => {
                            setHeld(row.symbol);
                        }}
                    >
                        <TileFace tile={faceOf(row)} />
                        <span className="letters-count">{`×${String(row.count)}`}</span>
                    </button>
                ))}
            </div>
            {chosen === null ? null : (
                <div className="letters-panel">
                    <div className="menu-row">
                        <span className="menu-label">{LETTER_POINTS}</span>
                        <Stepper
                            label={LETTER_POINTS}
                            value={chosen.value}
                            minimum={minimum}
                            maximum={maximum}
                            step={step}
                            disabled={readOnly}
                            onChange={(value): void => {
                                change(chosen.symbol, { value });
                            }}
                        />
                    </div>
                    <div className="menu-row">
                        <span className="menu-label">{LETTER_COUNT}</span>
                        <Stepper
                            label={LETTER_COUNT}
                            value={chosen.count}
                            minimum={minimum}
                            maximum={maximum}
                            step={step}
                            disabled={readOnly}
                            onChange={(count): void => {
                                change(chosen.symbol, { count });
                            }}
                        />
                    </div>
                    {categories.length > 1 ? (
                        <div className="menu-row">
                            <span className="menu-label">{LETTER_CATEGORY}</span>
                            <Picker
                                label={LETTER_CATEGORY}
                                value={chosen.category}
                                options={coloredOptions}
                                readOnly={readOnly}
                                onChange={(category): void => {
                                    change(chosen.symbol, { category });
                                }}
                            />
                        </div>
                    ) : null}
                </div>
            )}
            <p className="letters-total" role="status">
                {bagTotalCaption(bagTotal(rows, record?.blanks ?? 0))}
            </p>
        </>
    );
}

function faceOf(row: LetterRow): Tile {
    return {
        identifier: NO_IDENTIFIER,
        letter: row.symbol,
        value: row.value,
        category: row.category,
        blank: false,
    };
}

function pointsOf(rows: readonly LetterRow[], category: string): number {
    return rows.find((row) => row.category === category)?.value ?? 0;
}
