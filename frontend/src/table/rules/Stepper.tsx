import type { ReactElement } from "react";
import { useEffect, useState } from "react";

import { typedValue } from "../../play/rules/typed";
import { RULES_STEP_DOWN, RULES_STEP_UP } from "../strings";

export interface StepperProps {
    readonly label: string;
    readonly value: number;
    readonly minimum: number;
    readonly maximum: number;
    readonly step: number;
    readonly disabled: boolean;
    readonly onChange: (value: number) => void;
}

export function Stepper({ label, value, minimum, maximum, step, disabled, onChange }: StepperProps): ReactElement {
    const [typed, setTyped] = useState<string | null>(null);
    useEffect(() => {
        setTyped(null);
    }, [value]);
    const settle = (): void => {
        const asked = typed === null ? null : typedValue(typed, minimum, maximum);
        setTyped(null);
        if (asked !== null && asked !== value) {
            onChange(asked);
        }
    };
    return (
        <div className="stepper" role="group" aria-label={label}>
            <button
                type="button"
                className="stepper-step"
                aria-label={RULES_STEP_DOWN}
                disabled={disabled || value <= minimum}
                onClick={(): void => {
                    onChange(Math.max(minimum, value - step));
                }}
            >
                −
            </button>
            <input
                className="stepper-value"
                type="text"
                inputMode="numeric"
                aria-label={label}
                disabled={disabled}
                value={typed ?? String(value)}
                onChange={(change): void => {
                    setTyped(change.target.value);
                }}
                onBlur={settle}
                onKeyDown={(press): void => {
                    if (press.key === "Enter") {
                        press.currentTarget.blur();
                    }
                }}
            />
            <button
                type="button"
                className="stepper-step"
                aria-label={RULES_STEP_UP}
                disabled={disabled || value >= maximum}
                onClick={(): void => {
                    onChange(Math.min(maximum, value + step));
                }}
            >
                +
            </button>
        </div>
    );
}
