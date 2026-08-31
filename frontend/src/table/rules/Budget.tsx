import type { ReactElement } from "react";

import { budgetCaption, UNTIMED_CAPTION } from "../strings";

export interface BudgetProps {
    readonly label: string;
    readonly value: number | null;
    readonly offered: readonly number[];
    readonly unlimited: boolean;
    readonly readOnly: boolean;
    readonly onChange: (value: number | null) => void;
}

export function Budget({ label, value, offered, unlimited, readOnly, onChange }: BudgetProps): ReactElement {
    return (
        <select
            className="rules-select"
            disabled={readOnly}
            aria-label={label}
            value={value ?? ""}
            onChange={(change): void => {
                onChange(change.target.value === "" ? null : Number(change.target.value));
            }}
        >
            {unlimited ? <option value="">{UNTIMED_CAPTION}</option> : null}
            {offered.map((seconds) => (
                <option key={seconds} value={seconds}>
                    {budgetCaption(seconds)}
                </option>
            ))}
        </select>
    );
}
