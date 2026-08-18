import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { SettingsProvider } from "../../../src/play/settings/useSettings";
import { MotionToggle } from "../../../src/table/seats/MotionToggle";

describe("MotionToggle", () => {
    it("offers the motion choice as a quiet chip resting on the system setting", () => {
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <MotionToggle />
            </SettingsProvider>,
        );
        expect(markup).toContain('aria-label="Interface motion"');
        expect(markup).toContain("◐ Auto");
    });
});
