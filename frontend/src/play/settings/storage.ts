import { knownLocale } from "../device/locale";
import { knownMode } from "../device/mode";
import { knownMotion } from "../device/motion";
import { clearedLegacy, legacySettings } from "./legacy";
import type { Settings } from "./settings";
import { DEFAULT_SETTINGS } from "./settings";

export const SETTINGS_STORAGE_KEY = "slowiki-settings";

export type SettingsStorage = Pick<Storage, "getItem" | "setItem" | "removeItem">;

export function storedSettings(storage: SettingsStorage): Settings {
    const raw = storage.getItem(SETTINGS_STORAGE_KEY);
    if (raw !== null) {
        return parsedSettings(raw);
    }
    const adopted = legacySettings(storage);
    if (adopted === null) {
        return DEFAULT_SETTINGS;
    }
    rememberSettings(adopted, storage);
    clearedLegacy(storage);
    return adopted;
}

export function rememberSettings(settings: Settings, storage: Pick<Storage, "setItem">): void {
    storage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
}

export function currentSettings(): Settings {
    return typeof window === "undefined" ? DEFAULT_SETTINGS : storedSettings(window.localStorage);
}

export function parsedSettings(raw: string): Settings {
    const held = heldEntries(raw);
    return {
        mode: knownMode(textAt(held, "mode")) ?? DEFAULT_SETTINGS.mode,
        motion: knownMotion(textAt(held, "motion")) ?? DEFAULT_SETTINGS.motion,
        locale: knownLocale(textAt(held, "locale")),
        notices: flagAt(held, "notices") ?? DEFAULT_SETTINGS.notices,
    };
}

function heldEntries(raw: string): Record<string, unknown> {
    let parsed: unknown = null;
    try {
        parsed = JSON.parse(raw);
    } catch (error) {
        if (!(error instanceof SyntaxError)) {
            throw error;
        }
        return {};
    }
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
        return {};
    }
    return parsed as Record<string, unknown>;
}

function textAt(held: Record<string, unknown>, name: string): string | null {
    const value = held[name];
    return typeof value === "string" ? value : null;
}

function flagAt(held: Record<string, unknown>, name: string): boolean | null {
    const value = held[name];
    return typeof value === "boolean" ? value : null;
}
