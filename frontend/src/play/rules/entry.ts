import type { Offering } from "../../api/tables";
import type { RuleChanges } from "./changes";
import { NO_CHANGES } from "./changes";
import type { PresetBook } from "./preset";

export interface RulesEntry {
    readonly id: string;
    readonly label: string;
    readonly origin: string;
    readonly changes: RuleChanges;
    readonly saved: boolean;
    readonly offered: boolean;
}

export function entriesOf(offerings: readonly Offering[], book: PresetBook): readonly RulesEntry[] {
    const offered = new Set(offerings.map((offering) => offering.name));
    return [
        ...offerings.map(schemeEntry),
        ...book.presets.map((preset) => ({
            id: preset.id,
            label: preset.label,
            origin: preset.origin,
            changes: preset.changes,
            saved: true,
            offered: offered.has(preset.origin),
        })),
    ];
}

export function entryOf(entries: readonly RulesEntry[], id: string | null): RulesEntry | null {
    if (id === null) {
        return null;
    }
    return entries.find((entry) => entry.id === id) ?? null;
}

export function playableEntries(entries: readonly RulesEntry[]): readonly RulesEntry[] {
    return entries.filter((entry) => entry.offered);
}

function schemeEntry(offering: Offering): RulesEntry {
    return {
        id: offering.name,
        label: offering.name,
        origin: offering.name,
        changes: NO_CHANGES,
        saved: false,
        offered: true,
    };
}
