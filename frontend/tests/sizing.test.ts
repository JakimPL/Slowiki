import { describe, expect, it } from "vitest";

import { rowCountStyle } from "../src/table/sizing";

describe("rowCountStyle", () => {
    it("hands the row count to CSS as a custom property", () => {
        expect(rowCountStyle(7)).toEqual({ "--row-count": 7 });
    });

    it("keeps the count at least one so the CSS math never divides by zero", () => {
        expect(rowCountStyle(0)).toEqual({ "--row-count": 1 });
    });
});
