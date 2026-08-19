import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { CodeChip } from "../../../src/table/arrive/CodeChip";

describe("CodeChip", () => {
    it("offers the join code as a copy button", () => {
        const markup = renderToStaticMarkup(<CodeChip code="KWPZTR" />);
        expect(markup).toContain("<button");
        expect(markup).toContain('aria-label="Copy the table code"');
        expect(markup).toContain("KWPZTR");
        expect(markup).not.toContain("data-copied");
    });
});
