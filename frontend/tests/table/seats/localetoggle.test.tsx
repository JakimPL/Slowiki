import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { LocaleToggle } from "../../../src/table/seats/LocaleToggle";

describe("LocaleToggle", () => {
    it("prints the active language as a quiet chip", () => {
        const markup = renderToStaticMarkup(<LocaleToggle />);
        expect(markup).toContain('aria-label="Language"');
        expect(markup).toContain(">EN<");
    });
});
