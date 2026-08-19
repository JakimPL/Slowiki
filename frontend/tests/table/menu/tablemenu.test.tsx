import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { SettingsProvider } from "../../../src/play/settings/useSettings";
import { TableMenu } from "../../../src/table/menu/TableMenu";

const STAYS = (): void => {
    throw new Error("nobody leaves in a static render");
};

describe("TableMenu", () => {
    it("gathers the invitation, the device choices, and the way out", () => {
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <TableMenu table="t1" code="KWPZTR" onLeave={STAYS} onClose={STAYS} />
            </SettingsProvider>,
        );
        expect(markup).toContain('class="sheet menu" role="dialog" aria-label="Table"');
        expect(markup).toContain("Invitation");
        expect(markup).toContain("KWPZTR");
        expect(markup).toContain("Copy invitation");
        expect(markup).toContain("Turn notices");
        expect(markup).toContain("Sends a notification when your turn opens while this tab rests.");
        expect(markup).toContain("Color mode");
        expect(markup).toContain("Interface motion");
        expect(markup).toContain("Leave the table");
    });

    it("rests on the settings the device holds", () => {
        const markup = renderToStaticMarkup(
            <SettingsProvider>
                <TableMenu table="t1" code={null} onLeave={STAYS} onClose={STAYS} />
            </SettingsProvider>,
        );
        expect(markup).toContain('aria-pressed="true">Off</button>');
        expect(markup).toContain('aria-pressed="true">◐ Auto</button>');
        expect(markup).not.toContain("Invitation");
    });
});
