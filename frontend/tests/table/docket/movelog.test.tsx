import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { LogEntry } from "../../../src/play/story/log";
import { MoveLog } from "../../../src/table/docket/MoveLog";
import { aCompany } from "../../fixtures/positions";

const LOG: readonly LogEntry[] = [
    {
        seq: 0,
        actor: 0,
        kind: "play",
        words: [
            { text: "WÓZ", points: 30 },
            { text: "OS", points: 4 },
        ],
        points: 34,
        reason: null,
    },
    { seq: 1, actor: 1, kind: "pass", words: [], points: null, reason: null },
    { seq: 2, actor: 1, kind: "premove-returned", words: [], points: null, reason: "not_your_turn" },
];

describe("MoveLog", () => {
    it("lists the newest entry first with names and figures", () => {
        const markup = renderToStaticMarkup(<MoveLog log={LOG} company={aCompany()} onOpen={null} />);
        expect(markup).toContain('aria-label="Recent moves"');
        expect(markup).toContain("WÓZ, OS · 34");
        expect(markup).toContain("passed");
        expect(markup).toContain("premove returned · not your turn");
        expect(markup.indexOf("premove returned")).toBeLessThan(markup.indexOf("WÓZ, OS · 34"));
        expect(markup).toContain("Ala");
        expect(markup).toContain("Ola");
    });

    it("opens every played word where the panel is offered, keeping the score beside them", () => {
        const markup = renderToStaticMarkup(<MoveLog log={LOG} company={aCompany()} onOpen={() => undefined} />);
        expect(markup).toContain('class="log-word"');
        expect(markup).toContain('aria-label="Read WÓZ"');
        expect(markup).toContain('aria-label="Read OS"');
        expect(markup).toContain('aria-haspopup="dialog"');
        expect(markup).toContain(" · 34");
    });

    it("leaves the summary line as prose, since the disclosure owns that click", () => {
        const markup = renderToStaticMarkup(<MoveLog log={LOG} company={aCompany()} onOpen={() => undefined} />);
        expect(markup.slice(0, markup.indexOf("log-list"))).not.toContain("log-word");
    });

    it("prints passes and returned premoves as prose", () => {
        const markup = renderToStaticMarkup(<MoveLog log={LOG} company={aCompany()} onOpen={() => undefined} />);
        expect(markup).toContain("passed");
        expect(markup).toContain("premove returned · not your turn");
    });
});
