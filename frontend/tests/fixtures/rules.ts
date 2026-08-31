import type { RulesConfig } from "../../src/api/tables";
import { catalogOf } from "../../src/play/rules/catalog";
import { deviationsOf } from "../../src/play/rules/deviation";
import { entriesOf } from "../../src/play/rules/entry";
import { EMPTY_BOOK } from "../../src/play/rules/preset";
import type { Composing } from "../../src/play/rules/useComposing";
import { anAllowance, anOffering, someRules } from "./positions";

const NOTHING = (): void => undefined;

export const ALLOWANCES = [
    anAllowance({ setting: "seats", group: "table", kind: "count" }),
    anAllowance({
        setting: "total_seconds",
        group: "table",
        kind: "seconds",
        offered: [60, 600],
        unlimited: true,
        minimum: 30,
        maximum: 7200,
        step: 5,
    }),
    anAllowance({
        setting: "increment_seconds",
        group: "table",
        kind: "seconds",
        offered: [0, 15],
        minimum: 0,
        maximum: 300,
        step: 5,
    }),
    anAllowance({ setting: "premoves", group: "turns", kind: "toggle" }),
    anAllowance({
        setting: "bingo_tiles",
        group: "scoring",
        kind: "optional_count",
        unlimited: true,
        minimum: 1,
        maximum: 15,
        step: 1,
    }),
    anAllowance({
        setting: "board",
        group: "letters",
        kind: "choice",
        choices: ["literaki", "scrabble"],
        minimum: null,
        maximum: null,
        step: null,
    }),
];

export const RULES_CATALOG = catalogOf(ALLOWANCES);

export function aComposing(record: RulesConfig = someRules()): Composing {
    const standard = someRules();
    const entries = entriesOf([anOffering()], EMPTY_BOOK);
    return {
        catalog: RULES_CATALOG,
        entries,
        entry: entries[0] ?? null,
        standard,
        record,
        deviations: deviationsOf(record, standard, RULES_CATALOG),
        chooseEntry: NOTHING,
        setSetting: NOTHING,
        revert: NOTHING,
        revertAll: NOTHING,
    };
}
