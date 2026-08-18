import { describe, expect, it, vi } from "vitest";

import { buzzed, retitled, TURN_BUZZ } from "../../../src/play/device/alerts";

describe("retitled", () => {
    it("marks the tab while acting and restores it after", () => {
        expect(retitled("Literabble", true)).toBe("● Literabble — your turn");
        expect(retitled("Literabble", false)).toBe("Literabble");
    });
});

describe("buzzed", () => {
    it("vibrates only where the platform offers it", () => {
        const vibrate = vi.fn().mockReturnValue(true);
        buzzed({ vibrate }, TURN_BUZZ);
        expect(vibrate).toHaveBeenCalledWith([80, 40, 80]);
        expect(() => {
            buzzed({}, TURN_BUZZ);
        }).not.toThrow();
    });
});
