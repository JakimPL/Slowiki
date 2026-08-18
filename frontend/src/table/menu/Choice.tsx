import type { ReactElement } from "react";

export interface Option<Value> {
    readonly value: Value;
    readonly caption: string;
}

export interface ChoiceProps<Value> {
    readonly label: string;
    readonly note: string | null;
    readonly options: readonly Option<Value>[];
    readonly chosen: Value;
    readonly onChoose: (value: Value) => void;
}

export function Choice<Value extends string | boolean>({
    label,
    note,
    options,
    chosen,
    onChoose,
}: ChoiceProps<Value>): ReactElement {
    return (
        <div className="menu-row">
            <span className="menu-label">{label}</span>
            <div className="menu-options" role="group" aria-label={label}>
                {options.map((option) => (
                    <button
                        key={String(option.value)}
                        type="button"
                        className="menu-option"
                        aria-pressed={option.value === chosen}
                        onClick={(): void => {
                            onChoose(option.value);
                        }}
                    >
                        {option.caption}
                    </button>
                ))}
            </div>
            {note === null ? null : <p className="menu-note">{note}</p>}
        </div>
    );
}
