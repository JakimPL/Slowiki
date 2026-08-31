import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { Composing } from "../../../src/play/rules/useComposing";
import { SavedRules } from "../../../src/table/rules/SavedRules";
import { someRules } from "../../fixtures/positions";
import { aComposing } from "../../fixtures/rules";

function withPresets(presets: Composing["presets"]): Composing {
    return { ...aComposing(someRules({ premoves: false })), presets };
}

describe("SavedRules", () => {
    it("asks for a name and rests the save while none is given", () => {
        const markup = renderToStaticMarkup(<SavedRules composing={withPresets([])} />);
        expect(markup).toContain("Name these rules");
        expect(markup).toContain("Save");
        expect(markup).toContain('disabled=""');
        expect(markup).toContain("Nothing saved yet.");
    });

    it("puts a chosen record's own name in the field so saving renames it", () => {
        const composing = withPresets([]);
        const entry = {
            id: "preset-1",
            label: "House rules",
            origin: "literaki",
            changes: { premoves: false },
            saved: true,
            offered: true,
        };
        const markup = renderToStaticMarkup(
            <SavedRules composing={{ ...composing, entry, entries: [...composing.entries, entry] }} />,
        );
        expect(markup).toContain('value="House rules"');
    });

    it("lists each saved record with a way out and a way to copy it", () => {
        const markup = renderToStaticMarkup(
            <SavedRules
                composing={withPresets([
                    {
                        id: "preset-1",
                        label: "House rules",
                        origin: "literaki",
                        changes: { premoves: false },
                        saved: 1,
                    },
                ])}
            />,
        );
        expect(markup).toContain("House rules");
        expect(markup).toContain("Copy as text");
        expect(markup).toContain("Delete");
        expect(markup).not.toContain("no longer offered");
    });

    it("keeps a record whose game has gone, and says so", () => {
        const markup = renderToStaticMarkup(
            <SavedRules
                composing={withPresets([
                    {
                        id: "preset-2",
                        label: "Old rules",
                        origin: "retired",
                        changes: {},
                        saved: 1,
                    },
                ])}
            />,
        );
        expect(markup).toContain("Old rules");
        expect(markup).toContain("Delete");
        expect(markup).toContain("Its game is no longer offered.");
    });
});
