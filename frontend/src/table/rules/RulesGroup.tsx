import type { ReactElement } from "react";

import type { SettingGroup, SettingName } from "../../api/tables";
import type { RuleValue } from "../../play/rules/changes";
import type { Deviation } from "../../play/rules/deviation";
import { insideGroup } from "../../play/rules/deviation";
import { rowsOf } from "../../play/rules/rows";
import type { Composing } from "../../play/rules/useComposing";
import { GROUP_LABELS, rulesCaption, SETTING_LABELS } from "../strings";
import { RulesRow } from "./RulesRow";

export interface RulesGroupProps {
    readonly group: SettingGroup;
    readonly settings: readonly SettingName[];
    readonly composing: Composing;
    readonly deviations: readonly Deviation[];
    readonly open: boolean;
    readonly expert: boolean;
    readonly readOnly: boolean;
    readonly onToggle: () => void;
    readonly onOpenLetters: (() => void) | null;
}

export function RulesGroup({
    group,
    settings,
    composing,
    deviations,
    open,
    expert,
    readOnly,
    onToggle,
    onOpenLetters,
}: RulesGroupProps): ReactElement {
    const apart = insideGroup(deviations, group);
    const record = composing.record;
    const rows = record === null ? [] : rowsOf(settings, composing.catalog, record, apart, expert);
    return (
        <section className="rules-group" data-open={open ? "true" : undefined}>
            <button type="button" className="rules-group-head" aria-expanded={open} onClick={onToggle}>
                <span className="rules-group-name">{GROUP_LABELS[group]}</span>
                <span className="rules-group-state">{rulesCaption(apart.length)}</span>
            </button>
            {open ? (
                <div className="rules-group-rows">
                    {rows.map((row) => (
                        <RulesRow
                            key={row.setting}
                            control={row.control}
                            standard={row.standard}
                            readOnly={readOnly}
                            onChange={(value: RuleValue): void => {
                                composing.setSetting(row.setting, value);
                            }}
                            onRevert={(): void => {
                                composing.revert(row.setting);
                            }}
                        />
                    ))}
                    {onOpenLetters === null ? null : (
                        <button type="button" className="rules-row" onClick={onOpenLetters}>
                            <span className="rules-row-label">{SETTING_LABELS.letters}</span>
                            <span className="rules-row-state">{lettersCaption(composing)}</span>
                        </button>
                    )}
                </div>
            ) : null}
        </section>
    );
}

function lettersCaption(composing: Composing): string {
    const adjusted = Object.keys(composing.record?.letters ?? {}).length;
    return rulesCaption(adjusted);
}
