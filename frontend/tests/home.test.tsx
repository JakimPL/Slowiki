import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Home } from "../src/table/Home";

describe("Home", () => {
    it("prefills the invited code and waits for the offerings", () => {
        const markup = renderToStaticMarkup(
            <Home
                invitedCode="KWPZTR"
                themeNote={null}
                onArrive={() => {
                    throw new Error("nobody arrives in a static render");
                }}
            />,
        );
        expect(markup).toContain("Literabble");
        expect(markup).toContain('value="KWPZTR"');
        expect(markup).toContain("Reading the table offerings…");
        expect(markup).toContain("Join the table");
        expect(markup).toContain("Start the table");
    });
});
