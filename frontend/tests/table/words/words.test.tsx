import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { WordChip } from "../../../src/play/words/chips";
import { Words } from "../../../src/table/words/Words";

const CHIPS: readonly WordChip[] = [
    { text: "PIŁA", points: 7, status: "valid" },
    { text: "OSA", points: 3, status: "invalid" },
];

const OPEN = (): void => undefined;

describe("Words", () => {
    it("offers each chip as a button that announces the panel", () => {
        const markup = renderToStaticMarkup(<Words chips={CHIPS} bingo={0} openText={null} onOpen={OPEN} />);
        expect(markup).toContain('aria-label="Formed words"');
        expect(markup).toContain('<button type="button" class="word-chip" data-status="valid"');
        expect(markup).toContain('aria-haspopup="dialog"');
        expect(markup).toContain('aria-expanded="false"');
        expect(markup).toContain("PIŁA");
        expect(markup).toContain('<b class="word-points">7</b>');
    });

    it("marks the chip whose panel stands", () => {
        const markup = renderToStaticMarkup(<Words chips={CHIPS} bingo={0} openText="OSA" onOpen={OPEN} />);
        const opened = markup.slice(markup.indexOf("OSA") - 200, markup.indexOf("OSA"));
        expect(opened).toContain('data-open="true"');
        expect(opened).toContain('aria-expanded="true"');
        expect(markup.match(/data-open="true"/g)).toHaveLength(1);
    });

    it("leaves the chips inert where the table offers no lore", () => {
        const markup = renderToStaticMarkup(<Words chips={CHIPS} bingo={0} openText={null} onOpen={null} />);
        expect(markup).not.toContain("<button");
        expect(markup).toContain('<span class="word-chip" data-status="valid">');
    });

    it("keeps the bingo chip a span beside the words", () => {
        const markup = renderToStaticMarkup(<Words chips={CHIPS} bingo={50} openText={null} onOpen={OPEN} />);
        expect(markup).toContain('<span class="word-chip word-bingo" data-status="unknown">');
        expect(markup).toContain("Bingo");
        expect(markup.match(/<button/g)).toHaveLength(2);
    });
});
