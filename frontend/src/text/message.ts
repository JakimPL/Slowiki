import type { Catalog, Locale, PlainKey, PlainValues, PluralKey, PluralValues } from "./keys";
import { pluralCategory } from "./plural";

export type Values = Readonly<Record<string, string | number>>;

export type Given<Shape extends Values> = [keyof Shape] extends [never] ? [] : [values: Shape];

const PLACEHOLDER = /\{([a-z_]+)\}/g;

export function filled(template: string, values: Values): string {
    return template.replace(PLACEHOLDER, (_whole: string, name: string): string => substituted(template, values, name));
}

export function textFrom<Key extends PlainKey>(catalog: Catalog, key: Key, ...given: Given<PlainValues[Key]>): string {
    return filled(catalog.plain[key], given[0] ?? {});
}

export function countedFrom<Key extends PluralKey>(
    catalog: Catalog,
    locale: Locale,
    key: Key,
    count: number,
    ...given: Given<PluralValues[Key]>
): string {
    const category = pluralCategory(locale, count);
    return filled(catalog.plural[key][category], { ...given[0], count });
}

function substituted(template: string, values: Values, name: string): string {
    const value = values[name];
    if (value === undefined) {
        throw new Error(`Unknown placeholder ${name} in ${template}`);
    }
    return typeof value === "number" ? String(value) : value;
}
