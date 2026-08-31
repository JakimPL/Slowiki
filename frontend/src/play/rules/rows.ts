import type { RulesConfig, SettingName } from "../../api/tables";
import type { RulesCatalog } from "./catalog";
import type { Control } from "./control";
import { controlOf } from "./control";
import type { Deviation } from "./deviation";

export interface RuleRow {
    readonly setting: SettingName;
    readonly control: Control;
    readonly standard: Control | null;
}

export function rowsOf(
    settings: readonly SettingName[],
    catalog: RulesCatalog,
    record: RulesConfig,
    deviations: readonly Deviation[],
    expert: boolean,
): readonly RuleRow[] {
    return settings
        .map((setting) => rowOf(setting, catalog, record, deviations))
        .filter(isRow)
        .filter((row) => shown(row, catalog, expert));
}

export function holdsExpert(catalog: RulesCatalog): boolean {
    return catalog.allowances.some((allowance) => allowance.tier === "expert");
}

function isRow(row: RuleRow | null): row is RuleRow {
    return row !== null;
}

function rowOf(
    setting: SettingName,
    catalog: RulesCatalog,
    record: RulesConfig,
    deviations: readonly Deviation[],
): RuleRow | null {
    const allowance = catalog.bySetting.get(setting);
    if (allowance === undefined) {
        return null;
    }
    const control = controlOf(allowance, record);
    if (control === null || control.kind === "letters") {
        return null;
    }
    return {
        setting,
        control,
        standard: deviations.find((deviation) => deviation.setting === setting)?.standard ?? null,
    };
}

function shown(row: RuleRow, catalog: RulesCatalog, expert: boolean): boolean {
    if (catalog.bySetting.get(row.setting)?.tier !== "expert") {
        return true;
    }
    return expert || row.standard !== null;
}
