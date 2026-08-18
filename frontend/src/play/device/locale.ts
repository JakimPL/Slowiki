import type { Locale } from "../../text/keys";
import { DEFAULT_LOCALE, LOCALES } from "../../text/keys";

export const LOCALE_STORAGE_KEY = "literabble-locale";

const SUBTAG_SEPARATOR = "-";

export function knownLocale(raw: string | null): Locale | null {
    return LOCALES.find((candidate) => candidate === raw) ?? null;
}

export function storedLocale(storage: Pick<Storage, "getItem">): Locale | null {
    return knownLocale(storage.getItem(LOCALE_STORAGE_KEY));
}

export function preferredLocale(stored: Locale | null, languages: readonly string[]): Locale {
    if (stored !== null) {
        return stored;
    }
    for (const language of languages) {
        const spoken = knownLocale(primarySubtag(language));
        if (spoken !== null) {
            return spoken;
        }
    }
    return DEFAULT_LOCALE;
}

function primarySubtag(language: string): string {
    return language.split(SUBTAG_SEPARATOR)[0]?.toLowerCase() ?? "";
}

export function nextLocale(locale: Locale): Locale {
    const index = LOCALES.indexOf(locale);
    return LOCALES[(index + 1) % LOCALES.length] ?? locale;
}

export function rememberLocale(locale: Locale, storage: Pick<Storage, "setItem">): void {
    storage.setItem(LOCALE_STORAGE_KEY, locale);
}

export function appliedLocale(locale: Locale, root: HTMLElement): void {
    root.lang = locale;
}
