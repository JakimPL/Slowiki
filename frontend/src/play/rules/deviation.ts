import type { RulesConfig, SettingGroup, SettingName } from "../../api/tables";
import type { RulesCatalog } from "./catalog";
import { changedSettings } from "./changes";
import type { Control } from "./control";
import { controlOf } from "./control";

export interface Deviation {
    readonly setting: SettingName;
    readonly group: SettingGroup;
    readonly control: Control;
    readonly standard: Control;
}

export function deviationsOf(record: RulesConfig, standard: RulesConfig, catalog: RulesCatalog): readonly Deviation[] {
    return changedSettings(record, standard, catalog.settings)
        .map((setting) => deviationOf(setting, record, standard, catalog))
        .filter(isDeviation);
}

export function outsideGroup(deviations: readonly Deviation[], group: SettingGroup): readonly Deviation[] {
    return deviations.filter((deviation) => deviation.group !== group);
}

export function insideGroup(deviations: readonly Deviation[], group: SettingGroup): readonly Deviation[] {
    return deviations.filter((deviation) => deviation.group === group);
}

function isDeviation(deviation: Deviation | null): deviation is Deviation {
    return deviation !== null;
}

function deviationOf(
    setting: SettingName,
    record: RulesConfig,
    standard: RulesConfig,
    catalog: RulesCatalog,
): Deviation | null {
    const allowance = catalog.bySetting.get(setting);
    if (allowance === undefined) {
        return null;
    }
    const held = controlOf(allowance, record);
    const was = controlOf(allowance, standard);
    if (held === null || was === null) {
        return null;
    }
    return { setting, group: allowance.group, control: held, standard: was };
}
