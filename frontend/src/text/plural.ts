import type { Locale, PluralCategory } from "./keys";

type Rule = (count: number) => PluralCategory;

const FEW_LOWEST = 2;
const FEW_HIGHEST = 4;
const TEEN_LOWEST = 12;
const TEEN_HIGHEST = 14;
const UNIT_WRAP = 10;
const TEEN_WRAP = 100;

function englishCategory(count: number): PluralCategory {
    return count === 1 ? "one" : "other";
}

function polishCategory(count: number): PluralCategory {
    if (count === 1) {
        return "one";
    }
    const units = count % UNIT_WRAP;
    const teens = count % TEEN_WRAP;
    const few = units >= FEW_LOWEST && units <= FEW_HIGHEST;
    const teen = teens >= TEEN_LOWEST && teens <= TEEN_HIGHEST;
    return few && !teen ? "few" : "many";
}

const RULES: Record<Locale, Rule> = {
    en: englishCategory,
    pl: polishCategory,
};

export function pluralCategory(locale: Locale, count: number): PluralCategory {
    return RULES[locale](count);
}
