import { knownLocale } from "../device/locale";
import { knownMode } from "../device/mode";
import type { Settings } from "./settings";
import { DEFAULT_SETTINGS } from "./settings";

const MODE_KEY = "literabble-mode";
const LOCALE_KEY = "literabble-locale";
const NOTICES_KEY = "literabble-notices";
const NOTICES_WANTED = "on";

const KEYS: readonly string[] = [MODE_KEY, LOCALE_KEY, NOTICES_KEY];

export function legacySettings(storage: Pick<Storage, "getItem">): Settings | null {
    if (KEYS.every((key) => storage.getItem(key) === null)) {
        return null;
    }
    return {
        ...DEFAULT_SETTINGS,
        mode: knownMode(storage.getItem(MODE_KEY)) ?? DEFAULT_SETTINGS.mode,
        locale: knownLocale(storage.getItem(LOCALE_KEY)),
        notices: storage.getItem(NOTICES_KEY) === NOTICES_WANTED,
    };
}

export function clearedLegacy(storage: Pick<Storage, "removeItem">): void {
    for (const key of KEYS) {
        storage.removeItem(key);
    }
}
