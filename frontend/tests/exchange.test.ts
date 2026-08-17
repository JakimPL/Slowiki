import { describe, expect, it } from "vitest";

import { exchangeProspectOf } from "../src/play/exchange";
import { FALLBACK_RULES } from "../src/play/rules";
import { aView } from "./positions";

const RULES = { ...FALLBACK_RULES, exchangeLimit: 3, exchangeMinBag: 7 };

describe("exchangeProspectOf", () => {
    it("allows an exchange within the budget and the bag minimum", () => {
        const prospect = exchangeProspectOf(2, aView({ bag_count: 40, exchange_counts: { 0: 1 } }), 0, RULES);
        expect(prospect).toEqual({ count: 2, allowed: true, block: null, remaining: 2 });
    });

    it("blocks on a low bag before counting the budget", () => {
        const prospect = exchangeProspectOf(2, aView({ bag_count: 6, exchange_counts: { 0: 3 } }), 0, RULES);
        expect(prospect.block).toBe("bag-low");
        expect(prospect.allowed).toBe(false);
    });

    it("blocks once the exchange budget is spent", () => {
        const prospect = exchangeProspectOf(1, aView({ bag_count: 40, exchange_counts: { 0: 3 } }), 0, RULES);
        expect(prospect.block).toBe("limit-spent");
        expect(prospect.remaining).toBe(0);
    });

    it("treats a missing limit as unlimited", () => {
        const rules = { ...RULES, exchangeLimit: null };
        const prospect = exchangeProspectOf(1, aView({ bag_count: 40 }), 0, rules);
        expect(prospect).toEqual({ count: 1, allowed: true, block: null, remaining: null });
    });

    it("keeps an empty tray unarmed", () => {
        const prospect = exchangeProspectOf(0, aView({ bag_count: 40 }), 0, RULES);
        expect(prospect.allowed).toBe(false);
    });
});
