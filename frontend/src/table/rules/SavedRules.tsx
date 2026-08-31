import type { ReactElement } from "react";
import { useState } from "react";

import { useCopy } from "../../play/device/useCopy";
import type { SavedPreset } from "../../play/rules/preset";
import type { Composing } from "../../play/rules/useComposing";
import {
    COPIED_MARK,
    RULES_DELETE,
    RULES_EXPORT,
    RULES_RETIRED,
    RULES_SAVE_BUTTON,
    RULES_SAVE_LABEL,
    RULES_SAVE_PLACEHOLDER,
    RULES_SAVED_HEADING,
    RULES_SAVED_NONE,
} from "../strings";

const EXPORT_INDENT = 4;

export interface SavedRulesProps {
    readonly composing: Composing;
}

export function SavedRules({ composing }: SavedRulesProps): ReactElement {
    const [typed, setTyped] = useState<string | null>(null);
    const { copied, copy } = useCopy();
    const saved = composing.entry?.saved === true ? composing.entry : null;
    const label = typed ?? saved?.label ?? "";
    const named = label.trim();
    const renaming = saved !== null && named !== saved.label;
    const armed = named !== "" && (composing.unsaved || renaming);
    return (
        <section className="rules-saved">
            <h3 className="rules-saved-heading">{RULES_SAVED_HEADING}</h3>
            <div className="sheet-free">
                <label className="field">
                    <span>{RULES_SAVE_LABEL}</span>
                    <input
                        type="text"
                        value={label}
                        placeholder={RULES_SAVE_PLACEHOLDER}
                        onChange={(change): void => {
                            setTyped(change.target.value);
                        }}
                    />
                </label>
                <button
                    type="button"
                    className="action action-quiet"
                    disabled={!armed}
                    onClick={(): void => {
                        composing.savePreset(named);
                    }}
                >
                    {RULES_SAVE_BUTTON}
                </button>
            </div>
            {composing.presets.length === 0 ? (
                <p className="menu-note">{RULES_SAVED_NONE}</p>
            ) : (
                <ul className="rules-saved-list">
                    {composing.presets.map((preset) => (
                        <li key={preset.id} className="rules-saved-item">
                            <button
                                type="button"
                                className="rules-saved-name"
                                onClick={(): void => {
                                    composing.chooseEntry(preset.id);
                                }}
                            >
                                {preset.label}
                            </button>
                            <button
                                type="button"
                                className="rules-revert"
                                data-copied={copied ? "true" : undefined}
                                onClick={(): void => {
                                    copy(exported(preset));
                                }}
                            >
                                {copied ? COPIED_MARK : RULES_EXPORT}
                            </button>
                            <button
                                type="button"
                                className="rules-revert"
                                onClick={(): void => {
                                    composing.deletePreset(preset.id);
                                }}
                            >
                                {RULES_DELETE}
                            </button>
                            {offered(composing, preset) ? null : <p className="menu-note">{RULES_RETIRED}</p>}
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
}

function offered(composing: Composing, preset: SavedPreset): boolean {
    return composing.entries.some((entry) => !entry.saved && entry.origin === preset.origin);
}

function exported(preset: SavedPreset): string {
    return JSON.stringify({ label: preset.label, origin: preset.origin, changes: preset.changes }, null, EXPORT_INDENT);
}
