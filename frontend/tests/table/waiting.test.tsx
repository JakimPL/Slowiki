import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Waiting } from "../../src/table/Waiting";

const NOBODY = (): void => {
    throw new Error("nobody acts in a static render");
};

describe("Waiting", () => {
    it("waits quietly while the table is still answering", () => {
        const markup = renderToStaticMarkup(<Waiting note="Joining…" onLeave={null} />);
        expect(markup).toContain("Joining…");
        expect(markup).not.toContain("<button");
    });

    it("offers the way back when the table cannot be reached", () => {
        const markup = renderToStaticMarkup(<Waiting note="the table has closed" onLeave={NOBODY} />);
        expect(markup).toContain("the table has closed");
        expect(markup).toContain("Leave the table");
    });
});
