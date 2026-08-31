import type { ReactElement } from "react";

import type { RuleValue } from "../../play/rules/changes";
import type { Control } from "../../play/rules/control";
import type { Option } from "../menu/Options";
import { Options } from "../menu/Options";
import { RULES_REVERT, SETTING_LABELS, standardNote, VALUE_OFF, VALUE_ON, valueCaption } from "../strings";
import { Budget } from "./Budget";
import { OptionalCount } from "./OptionalCount";
import { Picker } from "./Picker";
import { Stepper } from "./Stepper";

const TOGGLE_OPTIONS: readonly Option<boolean>[] = [
    { value: true, caption: VALUE_ON },
    { value: false, caption: VALUE_OFF },
];

export interface RulesRowProps {
    readonly control: Control;
    readonly standard: Control | null;
    readonly readOnly: boolean;
    readonly onChange: (value: RuleValue) => void;
    readonly onRevert: () => void;
}

export function RulesRow({ control, standard, readOnly, onChange, onRevert }: RulesRowProps): ReactElement | null {
    const label = SETTING_LABELS[control.setting];
    const held = controlFor(control, label, readOnly, onChange);
    if (held === null) {
        return null;
    }
    return (
        <div className="rules-item" data-deviating={standard === null ? undefined : "true"}>
            <div className="rules-item-head">
                <span className="menu-label">{label}</span>
                {held}
            </div>
            <p className="rules-item-note">{standard === null ? "" : standardNote(valueCaption(standard))}</p>
            <button type="button" className="rules-revert" hidden={standard === null || readOnly} onClick={onRevert}>
                {RULES_REVERT}
            </button>
        </div>
    );
}

function controlFor(
    control: Control,
    label: string,
    readOnly: boolean,
    onChange: (value: RuleValue) => void,
): ReactElement | null {
    switch (control.kind) {
        case "toggle":
            return (
                <Options
                    label={label}
                    options={TOGGLE_OPTIONS}
                    chosen={control.value}
                    disabled={readOnly}
                    onChoose={onChange}
                />
            );
        case "count":
            return (
                <Stepper
                    label={label}
                    value={control.value}
                    minimum={control.minimum}
                    maximum={control.maximum}
                    step={control.step}
                    disabled={readOnly}
                    onChange={onChange}
                />
            );
        case "optional_count":
            return (
                <OptionalCount
                    label={label}
                    value={control.value}
                    minimum={control.minimum}
                    maximum={control.maximum}
                    step={control.step}
                    readOnly={readOnly}
                    onChange={onChange}
                />
            );
        case "choice":
            return (
                <Picker
                    label={label}
                    value={control.value}
                    choices={control.choices}
                    readOnly={readOnly}
                    onChange={onChange}
                />
            );
        case "seconds":
            return (
                <Budget
                    label={label}
                    value={control.value}
                    offered={control.offered}
                    unlimited={control.unlimited}
                    readOnly={readOnly}
                    onChange={onChange}
                />
            );
        case "letters":
            return null;
    }
}
