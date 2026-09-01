import type { ReactElement, SubmitEventHandler } from "react";

import type { RulesConfig, SettingAllowance, SettingName } from "../../api/tables";
import { outsideGroup } from "../../play/rules/deviation";
import { seatsOffered } from "../../play/rules/seats";
import type { Composing } from "../../play/rules/useComposing";
import { Help } from "../rules/Help";
import {
    budgetCaption,
    CREATE_BUTTON,
    CREATE_HEADING,
    deviationCaption,
    entryCaption,
    INCREMENT_LABEL,
    incrementCaption,
    OFFERINGS_LOADING,
    RULES_ROW_LABEL,
    RULES_UNTIMED,
    rulesCaption,
    SCHEME_LABEL,
    SEATS_LABEL,
    TIME_LABEL,
} from "../strings";

const CARD_GROUP = "table";

export interface CreateCardProps {
    readonly composing: Composing;
    readonly busy: boolean;
    readonly named: boolean;
    readonly onCreate: (record: RulesConfig, scheme: string) => void;
    readonly onOpenRules: () => void;
}

export function CreateCard({ composing, busy, named, onCreate, onOpenRules }: CreateCardProps): ReactElement {
    const { catalog, entries, entry, record, deviations } = composing;
    const hidden = outsideGroup(deviations, CARD_GROUP);
    const submit: SubmitEventHandler<HTMLFormElement> = (submission) => {
        submission.preventDefault();
        if (record !== null && entry !== null) {
            onCreate(record, entry.origin);
        }
    };
    return (
        <form className="panel" onSubmit={submit}>
            <h2>{CREATE_HEADING}</h2>
            {record === null || entry === null ? (
                <p className="panel-note">{OFFERINGS_LOADING}</p>
            ) : (
                <>
                    <label className="field">
                        <span>{SCHEME_LABEL}</span>
                        <select
                            value={entry.id}
                            onChange={(change): void => {
                                composing.chooseEntry(change.target.value);
                            }}
                        >
                            {entries.map((held) => (
                                <option key={held.id} value={held.id}>
                                    {entryCaption(held)}
                                </option>
                            ))}
                        </select>
                    </label>
                    <div className="field">
                        <div className="field-head reveal-host">
                            <label htmlFor="create-seats">{SEATS_LABEL}</label>
                            <Help setting="seats" />
                        </div>
                        <select
                            id="create-seats"
                            value={record.seats}
                            onChange={(change): void => {
                                composing.setSetting("seats", Number(change.target.value));
                            }}
                        >
                            {seatsOffered(record, allowanceOf(catalog.allowances, "seats")).map((count) => (
                                <option key={count} value={count}>
                                    {count}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="field-row">
                        <div className="field">
                            <div className="field-head reveal-host">
                                <label htmlFor="create-total">{TIME_LABEL}</label>
                                <Help setting="total_seconds" />
                            </div>
                            <select
                                id="create-total"
                                value={record.total_seconds ?? ""}
                                onChange={(change): void => {
                                    composing.setSetting(
                                        "total_seconds",
                                        change.target.value === "" ? null : Number(change.target.value),
                                    );
                                }}
                            >
                                <option value="">{RULES_UNTIMED}</option>
                                {rungsOf(catalog.allowances, "total_seconds").map((seconds) => (
                                    <option key={seconds} value={seconds}>
                                        {budgetCaption(seconds)}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="field">
                            <div className="field-head reveal-host">
                                <label htmlFor="create-increment">{INCREMENT_LABEL}</label>
                                <Help setting="increment_seconds" />
                            </div>
                            <select
                                id="create-increment"
                                value={record.increment_seconds}
                                disabled={record.total_seconds === null}
                                onChange={(change): void => {
                                    composing.setSetting("increment_seconds", Number(change.target.value));
                                }}
                            >
                                {rungsOf(catalog.allowances, "increment_seconds").map((seconds) => (
                                    <option key={seconds} value={seconds}>
                                        {incrementCaption(seconds)}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <button type="button" className="rules-row" onClick={onOpenRules}>
                        <span className="rules-row-label">{RULES_ROW_LABEL}</span>
                        <span className="rules-row-state">{rulesCaption(hidden.length)}</span>
                    </button>
                    {hidden.length === 0 ? null : (
                        <p className="rules-chips">
                            {hidden.map((deviation) => (
                                <span key={deviation.setting} className="rules-chip">
                                    {deviationCaption(deviation)}
                                </span>
                            ))}
                        </p>
                    )}
                </>
            )}
            <button type="submit" className="action" disabled={busy || !named || record === null}>
                {CREATE_BUTTON}
            </button>
        </form>
    );
}

function allowanceOf(allowances: readonly SettingAllowance[], setting: SettingName): SettingAllowance | null {
    return allowances.find((allowance) => allowance.setting === setting) ?? null;
}

function rungsOf(allowances: readonly SettingAllowance[], setting: SettingName): readonly number[] {
    return allowanceOf(allowances, setting)?.offered ?? [];
}
