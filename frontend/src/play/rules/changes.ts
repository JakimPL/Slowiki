import type { RulesConfig, SettingName } from "../../api/tables";

export type RuleChanges = Partial<RulesConfig>;
export type RuleValue = RulesConfig[keyof RulesConfig];
export type LetterAdjustments = RulesConfig["letters"];

export const NO_CHANGES: RuleChanges = {};

export function resolvedRules(
    standard: RulesConfig,
    changes: RuleChanges,
    allowed: Iterable<SettingName>,
): RulesConfig {
    let record = standard;
    for (const setting of allowed) {
        const value = changes[setting];
        if (value !== undefined) {
            record = { ...record, [setting]: value };
        }
    }
    return record;
}

export function changedSettings(
    record: RulesConfig,
    standard: RulesConfig,
    allowed: Iterable<SettingName>,
): readonly SettingName[] {
    return [...allowed].filter((setting) => !sameValue(record[setting], standard[setting]));
}

export function withSetting(
    changes: RuleChanges,
    standard: RulesConfig,
    setting: SettingName,
    value: RuleValue,
): RuleChanges {
    if (sameValue(value, standard[setting])) {
        return withoutSetting(changes, setting);
    }
    return { ...changes, [setting]: value };
}

export function withoutSetting(changes: RuleChanges, setting: SettingName): RuleChanges {
    let kept: RuleChanges = {};
    for (const [held, value] of Object.entries(changes)) {
        if (held !== setting) {
            kept = { ...kept, [held]: value };
        }
    }
    return kept;
}

export function sameValue(left: RuleValue, right: RuleValue): boolean {
    if (areAdjustments(left) && areAdjustments(right)) {
        return sameAdjustments(left, right);
    }
    return left === right;
}

function areAdjustments(value: RuleValue): value is LetterAdjustments {
    return typeof value === "object" && value !== null;
}

function sameAdjustments(left: LetterAdjustments, right: LetterAdjustments): boolean {
    const symbols = Object.keys(left);
    if (symbols.length !== Object.keys(right).length) {
        return false;
    }
    return symbols.every((symbol) => sameAdjustment(left[symbol], right[symbol]));
}

function sameAdjustment(
    left: LetterAdjustments[string] | undefined,
    right: LetterAdjustments[string] | undefined,
): boolean {
    if (left === undefined || right === undefined) {
        return false;
    }
    return (
        (left.value ?? null) === (right.value ?? null) &&
        (left.category ?? null) === (right.category ?? null) &&
        (left.count ?? null) === (right.count ?? null)
    );
}
