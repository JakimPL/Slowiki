import type { SettingAllowance, SettingGroup, SettingName } from "../../api/tables";

export interface SettingGroupRows {
    readonly group: SettingGroup;
    readonly settings: readonly SettingName[];
}

export interface RulesCatalog {
    readonly allowances: readonly SettingAllowance[];
    readonly settings: readonly SettingName[];
    readonly bySetting: ReadonlyMap<SettingName, SettingAllowance>;
    readonly groups: readonly SettingGroupRows[];
}

export const EMPTY_CATALOG: RulesCatalog = {
    allowances: [],
    settings: [],
    bySetting: new Map(),
    groups: [],
};

export function catalogOf(allowances: readonly SettingAllowance[]): RulesCatalog {
    return {
        allowances,
        settings: allowances.map((allowance) => allowance.setting),
        bySetting: new Map(allowances.map((allowance) => [allowance.setting, allowance])),
        groups: groupsOf(allowances),
    };
}

export function groupOf(catalog: RulesCatalog, group: SettingGroup): readonly SettingName[] {
    return catalog.groups.find((rows) => rows.group === group)?.settings ?? [];
}

function groupsOf(allowances: readonly SettingAllowance[]): readonly SettingGroupRows[] {
    const ordered: SettingGroup[] = [];
    const held = new Map<SettingGroup, SettingName[]>();
    for (const allowance of allowances) {
        const settings = held.get(allowance.group);
        if (settings === undefined) {
            ordered.push(allowance.group);
            held.set(allowance.group, [allowance.setting]);
            continue;
        }
        settings.push(allowance.setting);
    }
    return ordered.map((group) => ({ group, settings: held.get(group) ?? [] }));
}
