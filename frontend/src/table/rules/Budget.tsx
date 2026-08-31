import type { ReactElement } from "react";
import { useState } from "react";

import { budgetCaption, RULES_CUSTOM, RULES_CUSTOM_SPAN, RULES_UNTIMED } from "../strings";
import { Stepper } from "./Stepper";

const UNTIMED_VALUE = "";
const CUSTOM_VALUE = "custom";

export interface BudgetProps {
    readonly label: string;
    readonly value: number | null;
    readonly offered: readonly number[];
    readonly unlimited: boolean;
    readonly minimum: number;
    readonly maximum: number;
    readonly step: number;
    readonly readOnly: boolean;
    readonly onChange: (value: number | null) => void;
}

export function Budget({
    label,
    value,
    offered,
    unlimited,
    minimum,
    maximum,
    step,
    readOnly,
    onChange,
}: BudgetProps): ReactElement {
    const [asked, setAsked] = useState(false);
    const offLadder = value !== null && !offered.includes(value);
    const spanned = asked || offLadder;
    return (
        <div className="budget">
            <select
                className="rules-select"
                disabled={readOnly}
                aria-label={label}
                value={chosenOf(value, spanned)}
                onChange={(change): void => {
                    setAsked(change.target.value === CUSTOM_VALUE);
                    if (change.target.value !== CUSTOM_VALUE) {
                        onChange(change.target.value === UNTIMED_VALUE ? null : Number(change.target.value));
                    }
                }}
            >
                {unlimited ? <option value={UNTIMED_VALUE}>{RULES_UNTIMED}</option> : null}
                {offered.map((seconds) => (
                    <option key={seconds} value={seconds}>
                        {budgetCaption(seconds)}
                    </option>
                ))}
                <option value={CUSTOM_VALUE}>{RULES_CUSTOM}</option>
            </select>
            {spanned ? (
                <Stepper
                    label={RULES_CUSTOM_SPAN}
                    value={value ?? minimum}
                    minimum={minimum}
                    maximum={maximum}
                    step={step}
                    disabled={readOnly}
                    onChange={onChange}
                />
            ) : null}
        </div>
    );
}

function chosenOf(value: number | null, spanned: boolean): string {
    if (spanned) {
        return CUSTOM_VALUE;
    }
    return value === null ? UNTIMED_VALUE : String(value);
}
