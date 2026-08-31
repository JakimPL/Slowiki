import type { ReactElement } from "react";

import { asPills } from "../../play/rules/pills";
import { Options } from "../menu/Options";

export interface PickerProps {
    readonly label: string;
    readonly value: string;
    readonly choices: readonly string[];
    readonly readOnly: boolean;
    readonly onChange: (value: string) => void;
}

export function Picker({ label, value, choices, readOnly, onChange }: PickerProps): ReactElement {
    if (asPills(choices.length)) {
        return (
            <Options
                label={label}
                options={choices.map((choice) => ({ value: choice, caption: choice }))}
                chosen={value}
                disabled={readOnly}
                onChoose={onChange}
            />
        );
    }
    return (
        <select
            className="rules-select"
            disabled={readOnly}
            aria-label={label}
            value={value}
            onChange={(change): void => {
                onChange(change.target.value);
            }}
        >
            {choices.map((choice) => (
                <option key={choice} value={choice}>
                    {choice}
                </option>
            ))}
        </select>
    );
}
