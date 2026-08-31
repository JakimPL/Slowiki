import type { ReactElement } from "react";
import { useState } from "react";

import type { SettingGroup } from "../../api/tables";
import { holdsExpert } from "../../play/rules/rows";
import type { Composing } from "../../play/rules/useComposing";
import { useSheetFocus } from "../input/useSheetFocus";
import type { Option } from "../menu/Options";
import { Options } from "../menu/Options";
import {
    RULES_CLOSE,
    RULES_EXPERT_HIDDEN,
    RULES_EXPERT_LABEL,
    RULES_EXPERT_SHOWN,
    RULES_HEADING,
    RULES_REVERT_ALL,
} from "../strings";
import { LettersDepth } from "./LettersDepth";
import { RulesGroup } from "./RulesGroup";
import { SavedRules } from "./SavedRules";

const CARD_GROUP = "table";

const EXPERT_OPTIONS: readonly Option<boolean>[] = [
    { value: false, caption: RULES_EXPERT_HIDDEN },
    { value: true, caption: RULES_EXPERT_SHOWN },
];

export interface RulesSheetProps {
    readonly composing: Composing;
    readonly readOnly: boolean;
    readonly onClose: () => void;
}

export function RulesSheet({ composing, readOnly, onClose }: RulesSheetProps): ReactElement {
    const { catalog, deviations } = composing;
    const sheet = useSheetFocus<HTMLDivElement>();
    const [open, setOpen] = useState<readonly SettingGroup[]>(() => deviatingGroups(composing));
    const [expert, setExpert] = useState(false);
    const [editing, setEditing] = useState(false);
    const letters = catalog.bySetting.get("letters") ?? null;
    return (
        <div className="sheet-region">
            <button type="button" className="sheet-scrim" aria-label={RULES_CLOSE} onClick={onClose} />
            <div
                className="sheet rules-sheet"
                data-depth="1"
                role="dialog"
                aria-label={RULES_HEADING}
                tabIndex={-1}
                ref={sheet}
            >
                <h2 className="sheet-heading">{RULES_HEADING}</h2>
                {catalog.groups
                    .filter((rows) => rows.group !== CARD_GROUP)
                    .map((rows) => (
                        <RulesGroup
                            key={rows.group}
                            group={rows.group}
                            settings={rows.settings}
                            composing={composing}
                            deviations={deviations}
                            open={open.includes(rows.group)}
                            expert={expert}
                            readOnly={readOnly}
                            onToggle={(): void => {
                                setOpen((held) => toggled(held, rows.group));
                            }}
                            onOpenLetters={
                                rows.settings.includes("letters")
                                    ? (): void => {
                                          setEditing(true);
                                      }
                                    : null
                            }
                        />
                    ))}
                {readOnly ? null : <SavedRules composing={composing} />}
                {holdsExpert(catalog) ? (
                    <div className="menu-row">
                        <span className="menu-label">{RULES_EXPERT_LABEL}</span>
                        <Options
                            label={RULES_EXPERT_LABEL}
                            options={EXPERT_OPTIONS}
                            chosen={expert}
                            disabled={false}
                            onChoose={setExpert}
                        />
                    </div>
                ) : null}
                {readOnly ? null : (
                    <button
                        type="button"
                        className="action-quiet"
                        disabled={deviations.length === 0}
                        onClick={composing.revertAll}
                    >
                        {RULES_REVERT_ALL}
                    </button>
                )}
            </div>
            {editing && letters !== null ? (
                <LettersDepth
                    composing={composing}
                    readOnly={readOnly}
                    minimum={letters.minimum ?? 0}
                    maximum={letters.maximum ?? 0}
                    step={letters.step ?? 1}
                    onClose={(): void => {
                        setEditing(false);
                    }}
                />
            ) : null}
        </div>
    );
}

function deviatingGroups(composing: Composing): readonly SettingGroup[] {
    return [...new Set(composing.deviations.map((deviation) => deviation.group))].filter(
        (group) => group !== CARD_GROUP,
    );
}

function toggled(open: readonly SettingGroup[], group: SettingGroup): readonly SettingGroup[] {
    return open.includes(group) ? open.filter((held) => held !== group) : [...open, group];
}
