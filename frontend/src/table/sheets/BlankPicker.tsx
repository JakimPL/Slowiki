import type { ReactElement } from "react";
import { useState } from "react";

import type { Letter } from "../../api/tables";
import { BLANK_CONFIRM, BLANK_INPUT_LABEL, BLANK_PICKER_CLOSE, BLANK_PICKER_HEADING } from "../strings";

export interface BlankPickerProps {
    readonly alphabet: readonly Letter[] | null;
    readonly onPick: (symbol: string) => void;
    readonly onClose: () => void;
}

export function BlankPicker({ alphabet, onPick, onClose }: BlankPickerProps): ReactElement {
    return (
        <div className="sheet-region">
            <button type="button" className="sheet-scrim" aria-label={BLANK_PICKER_CLOSE} onClick={onClose} />
            <div className="sheet" role="dialog" aria-label={BLANK_PICKER_HEADING}>
                <h2 className="sheet-heading">{BLANK_PICKER_HEADING}</h2>
                {alphabet === null ? (
                    <FreeLetter onPick={onPick} />
                ) : (
                    <div className="sheet-grid">
                        {alphabet.map((letter) => (
                            <button
                                key={letter.symbol}
                                type="button"
                                className="sheet-letter"
                                onClick={(): void => {
                                    onPick(letter.symbol);
                                }}
                            >
                                {letter.symbol}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

interface FreeLetterProps {
    readonly onPick: (symbol: string) => void;
}

function FreeLetter({ onPick }: FreeLetterProps): ReactElement {
    const [symbol, setSymbol] = useState("");
    const cleaned = symbol.trim().toUpperCase();
    return (
        <div className="sheet-free">
            <label className="field">
                <span>{BLANK_INPUT_LABEL}</span>
                <input
                    type="text"
                    maxLength={1}
                    value={symbol}
                    onChange={(change): void => {
                        setSymbol(change.target.value);
                    }}
                />
            </label>
            <button
                type="button"
                className="action"
                disabled={cleaned === ""}
                onClick={(): void => {
                    onPick(cleaned);
                }}
            >
                {BLANK_CONFIRM}
            </button>
        </div>
    );
}
