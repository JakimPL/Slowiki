import type { SettingName } from "../../api/tables";
import type { RuleChanges, RuleValue } from "./changes";
import type { PresetBook, SavedPreset } from "./preset";
import { EMPTY_BOOK } from "./preset";

export const PRESETS_STORAGE_KEY = "slowiki-presets";

const ID_RADIX = 36;
const ID_FIRST = 2;
const ID_LAST = 8;

export type PresetStorage = Pick<Storage, "getItem" | "setItem">;

export function storedPresets(storage: Pick<Storage, "getItem">): PresetBook {
    return parsedPresets(storage.getItem(PRESETS_STORAGE_KEY));
}

export function rememberPresets(book: PresetBook, storage: Pick<Storage, "setItem">): void {
    storage.setItem(PRESETS_STORAGE_KEY, JSON.stringify(book));
}

export function parsedPresets(raw: string | null): PresetBook {
    if (raw === null) {
        return EMPTY_BOOK;
    }
    const held = heldRecord(parsedJson(raw));
    return {
        presets: heldList(held.presets).map(heldPreset).filter(isPreset),
        last: textAt(held, "last"),
    };
}

export function newPresetId(): string {
    const minted = Math.random().toString(ID_RADIX).slice(ID_FIRST, ID_LAST);
    return `preset-${Date.now().toString(ID_RADIX)}-${minted}`;
}

function isPreset(preset: SavedPreset | null): preset is SavedPreset {
    return preset !== null;
}

function heldPreset(entry: unknown): SavedPreset | null {
    const held = heldRecord(entry);
    const id = textAt(held, "id");
    const label = textAt(held, "label");
    const origin = textAt(held, "origin");
    if (id === null || label === null || origin === null) {
        return null;
    }
    return {
        id,
        label,
        origin,
        changes: heldChanges(held.changes),
        saved: numberAt(held, "saved") ?? 0,
    };
}

function heldChanges(entry: unknown): RuleChanges {
    let changes: RuleChanges = {};
    for (const [setting, value] of Object.entries(heldRecord(entry))) {
        changes = { ...changes, [setting as SettingName]: value as RuleValue };
    }
    return changes;
}

function parsedJson(raw: string): unknown {
    try {
        return JSON.parse(raw);
    } catch (error) {
        if (!(error instanceof SyntaxError)) {
            throw error;
        }
        return null;
    }
}

function heldRecord(held: unknown): Record<string, unknown> {
    if (typeof held !== "object" || held === null || Array.isArray(held)) {
        return {};
    }
    return held as Record<string, unknown>;
}

function heldList(held: unknown): readonly unknown[] {
    return Array.isArray(held) ? held : [];
}

function textAt(held: Record<string, unknown>, name: string): string | null {
    const value = held[name];
    return typeof value === "string" ? value : null;
}

function numberAt(held: Record<string, unknown>, name: string): number | null {
    const value = held[name];
    return typeof value === "number" ? value : null;
}
