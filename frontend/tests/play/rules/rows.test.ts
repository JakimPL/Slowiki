import { describe, expect, it } from "vitest";

import { catalogOf } from "../../../src/play/rules/catalog";
import { deviationsOf } from "../../../src/play/rules/deviation";
import { holdsExpert, rowsOf } from "../../../src/play/rules/rows";
import { anAllowance, someRules } from "../../fixtures/positions";
import { ALLOWANCES, RULES_CATALOG } from "../../fixtures/rules";

const SETTINGS = ["premoves", "bingo_tiles", "board", "letters"] as const;

describe("rowsOf", () => {
    it("carries one row per setting the catalog can draw", () => {
        const rows = rowsOf(SETTINGS, RULES_CATALOG, someRules(), [], false);
        expect(rows.map((row) => row.setting)).toEqual(["premoves", "bingo_tiles", "board"]);
        expect(rows.every((row) => row.standard === null)).toBe(true);
    });

    it("hands a deviating row the standard it left", () => {
        const record = someRules({ premoves: false });
        const deviations = deviationsOf(record, someRules(), RULES_CATALOG);
        const rows = rowsOf(SETTINGS, RULES_CATALOG, record, deviations, false);
        expect(rows[0]?.standard).toEqual({ kind: "toggle", setting: "premoves", value: true });
        expect(rows[1]?.standard).toBeNull();
    });

    it("keeps an expert row out of reach until it is revealed", () => {
        const catalog = catalogOf([anAllowance({ setting: "premoves", kind: "toggle", tier: "expert" })]);
        expect(rowsOf(["premoves"], catalog, someRules(), [], false)).toEqual([]);
        expect(rowsOf(["premoves"], catalog, someRules(), [], true)).toHaveLength(1);
    });

    it("shows an expert row that deviates whatever its tier", () => {
        const catalog = catalogOf([anAllowance({ setting: "premoves", kind: "toggle", tier: "expert" })]);
        const record = someRules({ premoves: false });
        const deviations = deviationsOf(record, someRules(), catalog);
        expect(rowsOf(["premoves"], catalog, record, deviations, false)).toHaveLength(1);
    });

    it("reads whether the catalog carries an expert setting at all", () => {
        expect(holdsExpert(RULES_CATALOG)).toBe(false);
        expect(holdsExpert(catalogOf([anAllowance({ tier: "expert" })]))).toBe(true);
        expect(ALLOWANCES.every((allowance) => allowance.tier !== "expert")).toBe(true);
    });
});
