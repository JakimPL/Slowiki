import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { SettingsProvider } from "../../../src/play/settings/useSettings";
import { LocaleToggle } from "../../../src/table/seats/LocaleToggle";

describe("LocaleToggle", () => {
    it("prints the active language as a quiet chip", () => {
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <LocaleToggle />
            </SettingsProvider>,
        );
        expect(markup).toContain('aria-label="Language"');
        expect(markup).toContain(">EN<");
    });
});
