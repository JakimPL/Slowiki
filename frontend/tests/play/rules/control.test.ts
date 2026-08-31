import { describe, expect, it } from "vitest";

import { controlOf } from "../../../src/play/rules/control";
import { anAllowance, someRules } from "../../fixtures/positions";

describe("controlOf", () => {
    it("reads a toggle from the record", () => {
        const control = controlOf(anAllowance({ setting: "premoves", kind: "toggle" }), someRules());
        expect(control).toEqual({ kind: "toggle", setting: "premoves", value: true });
    });

    it("carries the bounds a count moves between", () => {
        const control = controlOf(anAllowance({ setting: "seats", kind: "count" }), someRules());
        expect(control).toEqual({
            kind: "count",
            setting: "seats",
            value: 2,
            minimum: 1,
            maximum: 8,
            step: 1,
        });
    });

    it("keeps an unlimited count answerable with no value", () => {
        const allowance = anAllowance({
            setting: "exchange_limit",
            kind: "optional_count",
            unlimited: true,
            minimum: 0,
            maximum: 20,
        });
        expect(controlOf(allowance, someRules())).toEqual({
            kind: "optional_count",
            setting: "exchange_limit",
            value: 3,
            minimum: 0,
            maximum: 20,
            step: 1,
        });
        expect(controlOf(allowance, someRules({ exchange_limit: null }))?.kind).toBe("optional_count");
    });

    it("offers the choices the server discovered", () => {
        const allowance = anAllowance({
            setting: "board",
            kind: "choice",
            choices: ["literaki", "scrabble"],
            minimum: null,
            maximum: null,
            step: null,
        });
        expect(controlOf(allowance, someRules())).toEqual({
            kind: "choice",
            setting: "board",
            value: "literaki",
            choices: ["literaki", "scrabble"],
        });
    });

    it("offers the rungs a clock states", () => {
        const allowance = anAllowance({
            setting: "total_seconds",
            kind: "seconds",
            offered: [60, 600],
            unlimited: true,
            minimum: 30,
            maximum: 7200,
            step: 5,
        });
        expect(controlOf(allowance, someRules())).toEqual({
            kind: "seconds",
            setting: "total_seconds",
            value: null,
            offered: [60, 600],
            unlimited: true,
        });
    });

    it("opens its own surface for the letters", () => {
        const allowance = anAllowance({ setting: "letters", kind: "letters" });
        expect(controlOf(allowance, someRules())).toEqual({ kind: "letters", setting: "letters" });
    });

    it("drops an allowance whose kind the record contradicts", () => {
        expect(controlOf(anAllowance({ setting: "premoves", kind: "count" }), someRules())).toBeNull();
        expect(controlOf(anAllowance({ setting: "seats", kind: "count", minimum: null }), someRules())).toBeNull();
        expect(controlOf(anAllowance({ setting: "board", kind: "choice", choices: null }), someRules())).toBeNull();
    });
});
