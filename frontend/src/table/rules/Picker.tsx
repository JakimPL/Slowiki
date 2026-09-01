import type { ReactElement } from "react";

import { asPills } from "../../play/rules/pills";
import type { Option } from "../menu/Options";
import { Options } from "../menu/Options";

export interface PickerProps {
    readonly label: string;
    readonly value: string;
    readonly options: readonly Option<string>[];
    readonly readOnly: boolean;
    readonly onChange: (value: string) => void;
}

export function Picker({ label, value, options, readOnly, onChange }: PickerProps): ReactElement {
    if (asPills(options.length)) {
        return <Options label={label} options={options} chosen={value} disabled={readOnly} onChoose={onChange} />;
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
            {options.map((option) => (
                <option key={option.value} value={option.value}>
                    {option.caption}
                </option>
            ))}
        </select>
    );
}
