import { describe, expect, it } from "vitest";

import { legacySettings } from "../../../src/play/settings/legacy";
import { aStorage } from "../../fixtures/storage";

describe("legacy settings", () => {
    it("finds nothing on a device that never chose", () => {
        expect(legacySettings(aStorage())).toBeNull();
        expect(legacySettings(aStorage({ "slowiki-name": "Ala" }))).toBeNull();
    });

    it("reads one remembered choice and defaults its companions", () => {
        expect(legacySettings(aStorage({ "slowiki-notices": "on" }))).toEqual({
            mode: "system",
            motion: "system",
            locale: null,
            notices: true,
        });
    });

    it("refuses a choice the app no longer recognizes", () => {
        const held = legacySettings(aStorage({ "slowiki-mode": "sepia", "slowiki-locale": "kl" }));
        expect(held).toEqual({ mode: "system", motion: "system", locale: null, notices: false });
    });
});
