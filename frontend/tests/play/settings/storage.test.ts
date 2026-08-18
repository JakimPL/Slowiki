import { describe, expect, it } from "vitest";

import { DEFAULT_SETTINGS } from "../../../src/play/settings/settings";
import {
    parsedSettings,
    rememberSettings,
    SETTINGS_STORAGE_KEY,
    storedSettings,
} from "../../../src/play/settings/storage";
import { aStorage } from "../../fixtures/storage";

describe("settings storage", () => {
    it("starts a fresh device on the defaults and touches nothing", () => {
        const storage = aStorage();
        expect(storedSettings(storage)).toEqual(DEFAULT_SETTINGS);
        expect(storage.entries.size).toBe(0);
    });

    it("carries a whole record across visits", () => {
        const storage = aStorage();
        rememberSettings({ mode: "dark", motion: "calm", locale: "pl", notices: true }, storage);
        expect(storedSettings(storage)).toEqual({ mode: "dark", motion: "calm", locale: "pl", notices: true });
    });

    it("keeps the entries it understands and defaults the rest", () => {
        expect(parsedSettings('{"mode":"dark","motion":"loud","notices":"yes","tempo":3}')).toEqual({
            ...DEFAULT_SETTINGS,
            mode: "dark",
        });
    });

    it("falls back to the defaults on unreadable storage", () => {
        expect(parsedSettings("not json")).toEqual(DEFAULT_SETTINGS);
        expect(parsedSettings('["dark"]')).toEqual(DEFAULT_SETTINGS);
        expect(parsedSettings("null")).toEqual(DEFAULT_SETTINGS);
    });

    it("adopts the choices a previous version stored under its own keys", () => {
        const storage = aStorage({
            "literabble-mode": "dark",
            "literabble-locale": "pl",
            "literabble-notices": "on",
        });
        expect(storedSettings(storage)).toEqual({ mode: "dark", motion: "system", locale: "pl", notices: true });
        expect(storage.entries.has(SETTINGS_STORAGE_KEY)).toBe(true);
        expect(storage.entries.has("literabble-mode")).toBe(false);
        expect(storage.entries.has("literabble-locale")).toBe(false);
        expect(storage.entries.has("literabble-notices")).toBe(false);
    });

    it("adopts once and reads the record from then on", () => {
        const storage = aStorage({ "literabble-mode": "light" });
        expect(storedSettings(storage).mode).toBe("light");
        rememberSettings({ ...DEFAULT_SETTINGS, mode: "dark" }, storage);
        storage.setItem("literabble-mode", "light");
        expect(storedSettings(storage).mode).toBe("dark");
    });
});
