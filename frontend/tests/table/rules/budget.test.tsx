import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Budget } from "../../../src/table/rules/Budget";

const RUNGS = [30, 60, 90, 120, 180, 300, 600];
const NOTHING = (): void => undefined;

function markupOf(value: number | null): string {
    return renderToStaticMarkup(
        <Budget
            label="Time per turn"
            value={value}
            offered={RUNGS}
            unlimited={true}
            minimum={5}
            maximum={3600}
            step={5}
            readOnly={false}
            onChange={NOTHING}
        />,
    );
}

describe("Budget", () => {
    it("tells every rung apart", () => {
        const markup = markupOf(60);
        for (const caption of ["30 s", "1 min", "1 min 30 s", "2 min", "3 min", "5 min", "10 min"]) {
            expect(markup).toContain(`>${caption}<`);
        }
    });

    it("offers a span of its own beside the ladder", () => {
        expect(markupOf(60)).toContain("Custom…");
        expect(markupOf(60)).not.toContain("stepper-value");
    });

    it("holds a value off the ladder in its own field", () => {
        const markup = markupOf(137);
        expect(markup).toContain('value="custom"');
        expect(markup).toContain('value="137"');
        expect(markup).toContain('aria-label="Seconds"');
    });

    it("reads as untimed where the clock is lifted", () => {
        expect(markupOf(null)).toContain("untimed");
        expect(markupOf(null)).not.toContain("stepper-value");
    });
});
