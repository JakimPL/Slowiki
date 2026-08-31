import type { ReactElement } from "react";

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
            <span className="stepper-value" aria-live="polite">
                {value}
            </span>
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
