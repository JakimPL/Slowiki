import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Confirm } from "../../../src/table/rules/Confirm";

const NOTHING = (): void => undefined;

describe("Confirm", () => {
    it("says what is about to be lost and offers both answers", () => {
        const markup = renderToStaticMarkup(
            <Confirm
                asked={{
                    sentence: "Your unsaved changes to these rules will be lost.",
                    proceed: "Back to the standard rules",
                    onProceed: NOTHING,
                }}
                onKeep={NOTHING}
            />,
        );
        expect(markup).toContain('role="alertdialog"');
        expect(markup).toContain("Are you sure?");
        expect(markup).toContain("Your unsaved changes to these rules will be lost.");
        expect(markup).toContain("Keep them");
        expect(markup).toContain("Back to the standard rules");
    });
});
