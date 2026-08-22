import { describe, expect, it } from "vitest";

import { gathered } from "../../../src/play/seats/company";
import { aCompany, aSeatView } from "../../fixtures/positions";

describe("gathered", () => {
    it("holds once every seat is claimed", () => {
        expect(gathered(aCompany())).toBe(true);
        expect(gathered(aCompany([aSeatView(0), aSeatView(1, { claimed: false })]))).toBe(false);
    });
});
