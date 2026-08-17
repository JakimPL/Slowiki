import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { BlankPicker } from "../src/table/BlankPicker";

const NOOP = {
    onPick: (): void => undefined,
    onClose: (): void => undefined,
};

describe("BlankPicker", () => {
    it("offers the scheme's alphabet as a grid", () => {
        const alphabet = [
            { symbol: "A", value: 1, category: "yellow" },
            { symbol: "Ż", value: 5, category: "red" },
        ];
        const markup = renderToStaticMarkup(<BlankPicker alphabet={alphabet} {...NOOP} />);
        expect(markup).toContain('role="dialog"');
        expect(markup).toContain(">A</button>");
        expect(markup).toContain(">Ż</button>");
        expect(markup).not.toContain("<input");
    });

    it("falls back to a free letter input without a served alphabet", () => {
        const markup = renderToStaticMarkup(<BlankPicker alphabet={null} {...NOOP} />);
        expect(markup).toContain("<input");
        expect(markup).toContain("Assign the letter");
    });
});
