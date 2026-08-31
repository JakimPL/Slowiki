import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { LettersDepth } from "../../../src/table/rules/LettersDepth";
import { aComposing } from "../../fixtures/rules";

const NOTHING = (): void => undefined;

function markupOf(readOnly: boolean): string {
    return renderToStaticMarkup(
        <LettersDepth
            composing={aComposing()}
            minimum={0}
            maximum={99}
            step={1}
            readOnly={readOnly}
            onClose={NOTHING}
        />,
    );
}

describe("LettersDepth", () => {
    it("offers one way to keep the letters and one to drop them", () => {
        const markup = markupOf(false);
        expect(markup).toContain("Done");
        expect(markup).toContain("Cancel");
        expect(markup).toContain("letters-foot");
    });

    it("offers only a way out while the record is read-only", () => {
        const markup = markupOf(true);
        expect(markup).toContain("Close");
        expect(markup).not.toContain("Cancel");
        expect(markup).not.toContain(">Done<");
    });

    it("raises its scrim above the sheet it stands on", () => {
        expect(markupOf(false)).toContain("sheet-scrim sheet-scrim-deep");
    });
});
