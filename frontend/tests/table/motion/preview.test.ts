import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const SHEET = readFileSync(new URL("../../../src/styles.css", import.meta.url), "utf8");
const GUARDED = /@media \(hover: hover\) \{(?<body>[\s\S]*?)\n\}/;

function guarded(): string {
    return GUARDED.exec(SHEET)?.groups?.body ?? "";
}

describe("the help preview", () => {
    it("opens the note under a pointer that rests on the mark", () => {
        expect(guarded()).toContain(".rules-help:hover");
        expect(guarded()).toContain("~ .reveal");
    });

    it("keeps the preview on devices that can hover, so a tap never leaves it open", () => {
        expect(SHEET.replace(GUARDED, "")).not.toContain(".rules-help:hover");
    });

    it("leaves the keyboard the pin, which says whether it is open", () => {
        expect(guarded()).not.toContain(":focus-visible");
        expect(SHEET).toContain('.rules-help[aria-expanded="true"]');
    });
});
