import { describe, expect, it } from "vitest";

import { cssFor, declarationsFor } from "../../src/table/theme";
import { aStyle } from "../fixtures/payloads";

describe("declarationsFor", () => {
    it("turns every token group into custom properties", () => {
        const declarations = declarationsFor(aStyle().light);
        expect(declarations).toContain("--chrome-surface: #f3eddf;");
        expect(declarations).toContain("--board-surface: #ede5d1;");
        expect(declarations).toContain("--premium-word-2-fill: #d8cba8;");
        expect(declarations).toContain("--band-red: #ac4029;");
        expect(declarations).toContain("--accent-premove: #6d5e8e;");
    });

    it("prints the premium glyph as a watermark of its own fill", () => {
        const declarations = declarationsFor(aStyle().light);
        expect(declarations).toContain("--premium-word-2-glyph: #b5a784;");
        expect(declarations).toContain("--category-yellow-glyph: #ccb063;");
    });

    it("derives a tinted face per category from the band and the tint share", () => {
        const declarations = declarationsFor(aStyle().light);
        expect(declarations).toContain("--tile-face-yellow: #f5e7c5;");
        expect(declarations).toContain("--tile-face-red: #eed8c5;");
    });

    it("gives the blank a neutral band between the tile edge and the muted ink", () => {
        const declarations = declarationsFor(aStyle().light);
        expect(declarations).toContain("--band-blank: #a5987d;");
        expect(declarations).toContain("--tile-face-blank: #ede5d2;");
    });
});

describe("cssFor", () => {
    it("writes the light palette on the bare root", () => {
        const css = cssFor(aStyle());
        expect(css).toContain(":root {");
        expect(css).toContain("--chrome-surface: #f3eddf;");
    });

    it("guards the dark palette for system preference and stamps the explicit choice", () => {
        const css = cssFor(aStyle());
        expect(css).toContain("@media (prefers-color-scheme: dark)");
        expect(css).toContain(':root:not([data-mode="light"])');
        expect(css).toContain(':root[data-mode="dark"]');
        expect(css).toContain("--chrome-surface: #211b13;");
    });
});
