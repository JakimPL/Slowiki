import type { ReactElement } from "react";

export interface Option<Value> {
    readonly value: Value;
    readonly caption: string;
}

export interface OptionsProps<Value> {
    readonly label: string;
    readonly options: readonly Option<Value>[];
    readonly chosen: Value;
    readonly disabled: boolean;
    readonly onChoose: (value: Value) => void;
}

export function Options<Value extends string | number | boolean>({
    label,
    options,
    chosen,
    disabled,
    onChoose,
}: OptionsProps<Value>): ReactElement {
    return (
        <div className="menu-options" role="group" aria-label={label}>
            {options.map((option) => (
                <button
                    key={String(option.value)}
                    type="button"
                    className="menu-option"
                    aria-pressed={option.value === chosen}
                    disabled={disabled}
                    onClick={(): void => {
                        onChoose(option.value);
                    }}
                >
                    {option.caption}
                </button>
            ))}
        </div>
    );
}
