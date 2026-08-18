import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { SettingsProvider } from "../../../src/play/settings/useSettings";
import { Home } from "../../../src/table/arrive/Home";

const NOBODY = (): void => {
    throw new Error("nobody arrives in a static render");
};

describe("Home", () => {
    it("opens the join card with the prefilled code when invited", () => {
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Home invitedCode="KWPZTR" themeNote={null} onArrive={NOBODY} />
            </SettingsProvider>,
        );
        expect(markup).toContain("Literabble");
        expect(markup).toContain('value="KWPZTR"');
        expect(markup).toContain("Join the table");
        expect(markup).not.toContain("Start the table");
    });

    it("offers an invited visitor the way to a table of their own", () => {
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Home invitedCode="KWPZTR" themeNote={null} onArrive={NOBODY} />
            </SettingsProvider>,
        );
        expect(markup).toContain("Start your own table instead");
    });

    it("opens on the create card with a switch toward joining", () => {
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <Home invitedCode={null} themeNote={null} onArrive={NOBODY} />
            </SettingsProvider>,
        );
        expect(markup).toContain("Start the table");
        expect(markup).toContain("Reading the table offerings…");
        expect(markup).toContain("Have an invitation code?");
        expect(markup).not.toContain("Join the table");
    });
});
