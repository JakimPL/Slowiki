import { preferredLocale, storedLocale } from "../play/device/locale";
import { EN } from "./en";
import type { Catalogue, Locale, PlainKey, PlainValues, PluralKey, PluralValues } from "./keys";
import { DEFAULT_LOCALE } from "./keys";
import type { Given } from "./message";
import { countedFrom, textFrom } from "./message";
import { PL } from "./pl";

const CATALOGUES: Record<Locale, Catalogue> = {
    en: EN,
    pl: PL,
};

const LOCALE: Locale = resolvedLocale();

export function activeLocale(): Locale {
    return LOCALE;
}

export function text<Key extends PlainKey>(key: Key, ...given: Given<PlainValues[Key]>): string {
    return textFrom(CATALOGUES[LOCALE], key, ...given);
}

export function counted<Key extends PluralKey>(key: Key, count: number, ...given: Given<PluralValues[Key]>): string {
    return countedFrom(CATALOGUES[LOCALE], LOCALE, key, count, ...given);
}

function resolvedLocale(): Locale {
    if (typeof window === "undefined") {
        return DEFAULT_LOCALE;
    }
    return preferredLocale(storedLocale(window.localStorage), window.navigator.languages);
}
