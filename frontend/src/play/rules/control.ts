import type { RulesConfig, SettingAllowance, SettingName } from "../../api/tables";

export interface ToggleControl {
    readonly kind: "toggle";
    readonly setting: SettingName;
    readonly value: boolean;
}

export interface CountControl {
    readonly kind: "count";
    readonly setting: SettingName;
    readonly value: number;
    readonly minimum: number;
    readonly maximum: number;
    readonly step: number;
}

export interface OptionalCountControl {
    readonly kind: "optional_count";
    readonly setting: SettingName;
    readonly value: number | null;
    readonly minimum: number;
    readonly maximum: number;
    readonly step: number;
}

export interface ChoiceControl {
    readonly kind: "choice";
    readonly setting: SettingName;
    readonly value: string;
    readonly choices: readonly string[];
}

export interface SecondsControl {
    readonly kind: "seconds";
    readonly setting: SettingName;
    readonly value: number | null;
    readonly offered: readonly number[];
    readonly unlimited: boolean;
}

export interface LettersControl {
    readonly kind: "letters";
    readonly setting: SettingName;
}

export type Control =
    ToggleControl | CountControl | OptionalCountControl | ChoiceControl | SecondsControl | LettersControl;

export function controlOf(allowance: SettingAllowance, record: RulesConfig): Control | null {
    const value = record[allowance.setting];
    switch (allowance.kind) {
        case "toggle":
            return typeof value === "boolean" ? { kind: "toggle", setting: allowance.setting, value } : null;
        case "count":
            return typeof value === "number" ? countedControl(allowance, value) : null;
        case "optional_count":
            return typeof value === "number" || value === null ? optionalControl(allowance, value) : null;
        case "choice":
            return typeof value === "string" ? chosenControl(allowance, value) : null;
        case "seconds":
            return typeof value === "number" || value === null ? secondsControl(allowance, value) : null;
        case "letters":
            return { kind: "letters", setting: allowance.setting };
    }
}

function countedControl(allowance: SettingAllowance, value: number): CountControl | null {
    const bounded = boundsOf(allowance);
    return bounded === null ? null : { kind: "count", setting: allowance.setting, value, ...bounded };
}

function optionalControl(allowance: SettingAllowance, value: number | null): OptionalCountControl | null {
    const bounded = boundsOf(allowance);
    if (bounded === null || !allowance.unlimited) {
        return null;
    }
    return { kind: "optional_count", setting: allowance.setting, value, ...bounded };
}

function chosenControl(allowance: SettingAllowance, value: string): ChoiceControl | null {
    if (allowance.choices === null) {
        return null;
    }
    return { kind: "choice", setting: allowance.setting, value, choices: allowance.choices };
}

function secondsControl(allowance: SettingAllowance, value: number | null): SecondsControl | null {
    if (allowance.offered === null) {
        return null;
    }
    return {
        kind: "seconds",
        setting: allowance.setting,
        value,
        offered: allowance.offered,
        unlimited: allowance.unlimited,
    };
}

function boundsOf(
    allowance: SettingAllowance,
): { readonly minimum: number; readonly maximum: number; readonly step: number } | null {
    const { minimum, maximum, step } = allowance;
    if (minimum === null || maximum === null || step === null) {
        return null;
    }
    return { minimum, maximum, step };
}
