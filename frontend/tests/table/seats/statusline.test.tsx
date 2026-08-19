import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { StatusLine } from "../../../src/table/seats/StatusLine";

const NOBODY = (): void => {
    throw new Error("nobody opens the standing in a static render");
};

describe("StatusLine", () => {
    it("announces the turn as a live region while the game runs", () => {
        const markup = renderToStaticMarkup(<StatusLine text="Your turn" tone="acting" onOpen={null} />);
        expect(markup).toContain('role="status"');
        expect(markup).toContain('data-tone="acting"');
        expect(markup).not.toContain("<button");
    });

    it("becomes the way back to the final standing", () => {
        const markup = renderToStaticMarkup(<StatusLine text="Ola wins with 312" tone="over" onOpen={NOBODY} />);
        expect(markup).toContain("<button");
        expect(markup).toContain('title="Show the final standing"');
        expect(markup).toContain("Ola wins with 312");
    });
});
