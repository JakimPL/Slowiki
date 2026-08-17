import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { LogEntry } from "../src/play/log";
import { MoveLog } from "../src/table/MoveLog";
import { aCompany } from "./positions";

const LOG: readonly LogEntry[] = [
    { seq: 0, actor: 0, kind: "play", words: [{ text: "WÓZ", points: 34 }], points: 34, reason: null },
    { seq: 1, actor: 1, kind: "pass", words: [], points: null, reason: null },
    { seq: 2, actor: 1, kind: "premove-returned", words: [], points: null, reason: "not_your_turn" },
];

describe("MoveLog", () => {
    it("lists the newest entry first with names and figures", () => {
        const markup = renderToStaticMarkup(<MoveLog log={LOG} company={aCompany()} />);
        expect(markup).toContain('aria-label="Recent moves"');
        expect(markup).toContain("WÓZ · 34");
        expect(markup).toContain("passed");
        expect(markup).toContain("premove returned · not your turn");
        expect(markup.indexOf("premove returned")).toBeLessThan(markup.indexOf("WÓZ · 34"));
        expect(markup).toContain("Ala");
        expect(markup).toContain("Ola");
    });
});
