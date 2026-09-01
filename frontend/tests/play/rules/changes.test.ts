import { describe, expect, it } from "vitest";

import {
    changedSettings,
    resolvedRules,
    sameValue,
    withoutSetting,
    withSetting,
} from "../../../src/play/rules/changes";
import { someRules } from "../../fixtures/positions";

const SETTINGS = ["seats", "exchange_limit", "letters", "premoves"] as const;

describe("resolvedRules", () => {
    it("lays the changes over the standard record", () => {
        const record = resolvedRules(someRules(), { seats: 4, exchange_limit: null }, SETTINGS);
        expect(record.seats).toBe(4);
        expect(record.exchange_limit).toBeNull();
        expect(record.rack_size).toBe(7);
    });

    it("ignores a change no allowance covers", () => {
        const record = resolvedRules(someRules(), { seats: 4, premoves: false }, ["seats"]);
        expect(record.seats).toBe(4);
        expect(record.premoves).toBe(true);
    });

    it("answers the standard record where nothing changed", () => {
        expect(resolvedRules(someRules(), {}, SETTINGS)).toEqual(someRules());
    });
});

describe("changedSettings", () => {
    it("names what a record changed", () => {
        const record = someRules({ seats: 4, letters: { Ź: { value: 12 } } });
        expect(changedSettings(record, someRules(), SETTINGS)).toEqual(["seats", "letters"]);
    });

    it("counts an equal letter table as unchanged", () => {
        const record = someRules({ letters: {} });
        expect(changedSettings(record, someRules(), SETTINGS)).toEqual([]);
    });

    it("reads a letter adjustment that differs in one field", () => {
        const standard = someRules({ letters: { Ź: { value: 12, count: 3 } } });
        const record = someRules({ letters: { Ź: { value: 12, count: 2 } } });
        expect(changedSettings(record, standard, SETTINGS)).toEqual(["letters"]);
    });
});

describe("withSetting", () => {
    it("keeps a change that differs from the standard", () => {
        expect(withSetting({}, someRules(), "seats", 4)).toEqual({ seats: 4 });
    });

    it("drops a change that returns to the standard", () => {
        const changes = withSetting({}, someRules(), "seats", 4);
        expect(withSetting(changes, someRules(), "seats", 2)).toEqual({});
    });

    it("reverts one setting and leaves the rest", () => {
        const changes = { seats: 4, premoves: false };
        expect(withoutSetting(changes, "seats")).toEqual({ premoves: false });
    });
});

describe("sameValue", () => {
    it("tells a missing adjustment from a stated one", () => {
        expect(sameValue({ A: { value: 1 } }, {})).toBe(false);
        expect(sameValue({ A: { value: 1 } }, { A: { value: 1, category: null } })).toBe(true);
        expect(sameValue(null, null)).toBe(true);
        expect(sameValue(7, null)).toBe(false);
    });
});
