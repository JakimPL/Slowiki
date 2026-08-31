import type { ReactElement } from "react";

import type { Option } from "../menu/Options";
import { Options } from "../menu/Options";
import { RULES_LIMITED, RULES_UNLIMITED } from "../strings";
import { Stepper } from "./Stepper";

const LIMIT_OPTIONS: readonly Option<boolean>[] = [
    { value: true, caption: RULES_LIMITED },
    { value: false, caption: RULES_UNLIMITED },
];

export interface OptionalCountProps {
    readonly label: string;
    readonly value: number | null;
    readonly minimum: number;
    readonly maximum: number;
    readonly step: number;
    readonly onChange: (value: number | null) => void;
}

export function OptionalCount({ label, value, minimum, maximum, step, onChange }: OptionalCountProps): ReactElement {
    return (
        <div className="optional-count">
            <Options
                label={label}
                options={LIMIT_OPTIONS}
                chosen={value !== null}
                disabled={false}
                onChoose={(limited): void => {
                    onChange(limited ? minimum : null);
                }}
            />
            <Stepper
                label={label}
                value={value ?? minimum}
                minimum={minimum}
                maximum={maximum}
                step={step}
                disabled={value === null}
                onChange={onChange}
            />
        </div>
    );
}
