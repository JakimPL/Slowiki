import type { ReactElement } from "react";

import type { Option } from "./Options";
import { Options } from "./Options";

export interface ChoiceProps<Value> {
    readonly label: string;
    readonly note: string | null;
    readonly options: readonly Option<Value>[];
    readonly chosen: Value;
    readonly onChoose: (value: Value) => void;
}

export function Choice<Value extends string | number | boolean>({
    label,
    note,
    options,
    chosen,
    onChoose,
}: ChoiceProps<Value>): ReactElement {
    return (
        <div className="menu-row">
            <span className="menu-label">{label}</span>
            <Options label={label} options={options} chosen={chosen} disabled={false} onChoose={onChoose} />
            {note === null ? null : <p className="menu-note">{note}</p>}
        </div>
    );
}
