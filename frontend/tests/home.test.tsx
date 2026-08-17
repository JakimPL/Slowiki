import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Home } from "../src/table/Home";

const NOBODY = (): void => {
    throw new Error("nobody arrives in a static render");
};

describe("Home", () => {
    it("shows only the join card with the prefilled code when invited", () => {
        const markup = renderToStaticMarkup(<Home invitedCode="KWPZTR" themeNote={null} onArrive={NOBODY} />);
        expect(markup).toContain("Literabble");
        expect(markup).toContain('value="KWPZTR"');
        expect(markup).toContain("Join the table");
        expect(markup).not.toContain("Start the table");
        expect(markup).not.toContain("Have an invitation code?");
    });

    it("opens on the create card with a switch toward joining", () => {
        const markup = renderToStaticMarkup(<Home invitedCode={null} themeNote={null} onArrive={NOBODY} />);
        expect(markup).toContain("Start the table");
        expect(markup).toContain("Reading the table offerings…");
        expect(markup).toContain("Have an invitation code?");
        expect(markup).not.toContain("Join the table");
    });
});
