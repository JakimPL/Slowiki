import { describe, expect, it } from "vitest";

import { innermost } from "../../../src/play/rules/ladder";

const NONE = { confirm: false, letters: false, inspected: false, rules: false };

describe("innermost", () => {
    it("answers the layer a retreat closes first", () => {
        expect(innermost({ ...NONE, confirm: true, letters: true, rules: true })).toBe("confirm");
        expect(innermost({ ...NONE, letters: true, rules: true })).toBe("letters");
        expect(innermost({ ...NONE, inspected: true })).toBe("inspected");
        expect(innermost({ ...NONE, rules: true })).toBe("rules");
    });

    it("answers nothing while nothing is open", () => {
        expect(innermost(NONE)).toBeNull();
    });

    it("closes the letters before the sheet they stand on", () => {
        expect(innermost({ ...NONE, letters: true, inspected: true })).toBe("letters");
    });
});
