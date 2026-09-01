import { describe, expect, it } from "vitest";

import { seatsOffered } from "../../../src/play/rules/seats";
import { anAllowance, someRules } from "../../fixtures/positions";

describe("seatsOffered", () => {
    it("offers the whole span a table allows", () => {
        expect(seatsOffered(someRules(), anAllowance({ minimum: 1, maximum: 8 }))).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
    });

    it("seats one player where the rack takes the whole bag", () => {
        const rules = someRules({ rack_size: null, seats: 1, pass_end_rounds: null });
        expect(seatsOffered(rules, anAllowance({ minimum: 1, maximum: 8 }))).toEqual([1]);
    });

    it("seats one player before the offerings arrive", () => {
        expect(seatsOffered(null, null)).toEqual([1]);
        expect(seatsOffered(someRules(), null)).toEqual([1]);
    });
});
