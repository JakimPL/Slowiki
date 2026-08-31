import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Reveal } from "../../../src/table/motion/Reveal";

function markupOf(open: boolean): string {
    return renderToStaticMarkup(
        <Reveal open={open} id="a-note">
            <span>the note</span>
        </Reveal>,
    );
}

describe("Reveal", () => {
    it("states on the growing element whether it is open", () => {
        expect(markupOf(true)).toContain('class="reveal" data-open="true"');
        expect(markupOf(false)).not.toContain("data-open");
    });

    it("names the region it opens so a control can point at it", () => {
        expect(markupOf(true)).toContain('class="reveal-body" id="a-note"');
        expect(markupOf(false)).toContain('class="reveal-body" id="a-note"');
    });

    it("holds its content through both states so the region has a height to grow to", () => {
        expect(markupOf(true)).toContain("the note");
        expect(markupOf(false)).toContain("the note");
    });
});
