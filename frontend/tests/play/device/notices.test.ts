import { describe, expect, it } from "vitest";

import { noticeDue } from "../../../src/play/device/notices";

describe("notices", () => {
    it("posts only for my turn on a resting tab with permission", () => {
        expect(noticeDue(true, true, true, "granted")).toBe(true);
        expect(noticeDue(false, true, true, "granted")).toBe(false);
        expect(noticeDue(true, false, true, "granted")).toBe(false);
        expect(noticeDue(true, true, false, "granted")).toBe(false);
        expect(noticeDue(true, true, true, "denied")).toBe(false);
    });
});
