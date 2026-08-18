import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Choice } from "../../../src/table/menu/Choice";

const OPTIONS = [
    { value: "system", caption: "Auto" },
    { value: "light", caption: "Light" },
    { value: "dark", caption: "Dark" },
];

const HOLDS = (): void => {
    throw new Error("nothing is chosen in a static render");
};

describe("Choice", () => {
    it("names the setting and presses the option that holds", () => {
        const markup = renderToStaticMarkup(
            <Choice label="Color mode" note={null} options={OPTIONS} chosen="dark" onChoose={HOLDS} />,
        );
        expect(markup).toContain('<span class="menu-label">Color mode</span>');
        expect(markup).toContain('role="group" aria-label="Color mode"');
        expect(markup).toContain('aria-pressed="true">Dark</button>');
        expect(markup).toContain('aria-pressed="false">Auto</button>');
        expect(markup).not.toContain("menu-note");
    });

    it("carries a note under the options when the setting needs a sentence", () => {
        const markup = renderToStaticMarkup(
            <Choice
                label="Turn notices"
                note="Sends a notification."
                options={[
                    { value: false, caption: "Off" },
                    { value: true, caption: "On" },
                ]}
                chosen={false}
                onChoose={HOLDS}
            />,
        );
        expect(markup).toContain('<p class="menu-note">Sends a notification.</p>');
        expect(markup).toContain('aria-pressed="true">Off</button>');
    });
});
