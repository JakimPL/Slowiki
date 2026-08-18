import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { loreFor, SAMPLE_SOURCE } from "../../../src/play/lore/lore";
import type { LoreAnswer } from "../../../src/play/lore/readings";
import { NO_LORE_ANSWER } from "../../../src/play/lore/readings";
import type { WordChip } from "../../../src/play/words/chips";
import { WordPanel } from "../../../src/table/words/WordPanel";
import { aForm, aLore, aReading, someInflection } from "../../fixtures/lore";

const CHIP: WordChip = { text: "PIŁA", points: 7, status: "valid" };
const CLOSE = (): void => undefined;

function cardOf(chip: WordChip, answer: LoreAnswer): string {
    return renderToStaticMarkup(<WordPanel chip={chip} answer={answer} onClose={CLOSE} />);
}

function readyWith(lore: LoreAnswer["lore"], sample: boolean): LoreAnswer {
    return { state: "ready", lore, sample };
}

describe("WordPanel", () => {
    it("stands in the sheet stratum as a dialog for the word it opened for", () => {
        const markup = cardOf(CHIP, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE));
        expect(markup).toContain('class="sheet-region"');
        expect(markup).toContain('class="sheet-scrim"');
        expect(markup).toContain('aria-label="Close the word panel"');
        expect(markup).toContain('role="dialog"');
        expect(markup).toContain('data-depth="card"');
        expect(markup).toContain('aria-label="PIŁA — dictionary reading"');
        expect(markup).toContain(">PIŁA</h2>");
        expect(markup).toContain(">7</span>");
    });

    it("stacks a homonym's readings, each with its part, base form and odmiana", () => {
        const markup = cardOf(CHIP, readyWith(loreFor("PIŁA", true), SAMPLE_SOURCE));
        expect(markup).toContain(">rzeczownik</span>piła");
        expect(markup).toContain("mianownik · pojedyncza · żeński");
        expect(markup).toContain(">czasownik</span>pić");
        expect(markup).toContain("forma przeszła");
        expect(markup.match(/class="word-reading"/g)).toHaveLength(2);
    });

    it("badges sample data and rests once the answer is served", () => {
        expect(cardOf(CHIP, readyWith(aLore(), true))).toContain("sample data");
        expect(cardOf(CHIP, readyWith(aLore(), false))).not.toContain("sample data");
    });

    it("carries the dictionary's verdict, and stays silent while it is unknown", () => {
        expect(cardOf(CHIP, readyWith(aLore(), false))).toContain("in the dictionary");
        const unknown = cardOf({ ...CHIP, status: "unknown" }, readyWith(aLore(), false));
        expect(unknown).not.toContain("word-verdict");
    });

    it("reads a refused word as a note, with no reading to show", () => {
        const markup = cardOf({ ...CHIP, status: "invalid" }, readyWith(loreFor("PIŁA", false), SAMPLE_SOURCE));
        expect(markup).toContain("not in the dictionary");
        expect(markup).toContain("there is no reading");
        expect(markup).not.toContain("word-reading");
    });

    it("says plainly that a playable word carries no analysis", () => {
        const markup = cardOf(CHIP, readyWith(aLore({ readings: [] }), false));
        expect(markup).toContain("no analysis");
        expect(markup).toContain("The word plays.");
    });

    it("prints one odmiana line per bundle the asked form stands in", () => {
        const syncretic = aReading({
            forms: [
                aForm({ tags: someInflection({ cases: ["mianownik"], number: "pojedyncza" }) }),
                aForm({ tags: someInflection({ cases: ["wołacz"], number: "pojedyncza" }) }),
                aForm({ text: "PIŁY", tags: someInflection({ cases: ["dopełniacz"], number: "pojedyncza" }) }),
            ],
        });
        const markup = cardOf(CHIP, readyWith(aLore({ readings: [syncretic] }), false));
        expect(markup).toContain("mianownik · pojedyncza");
        expect(markup).toContain("wołacz · pojedyncza");
        expect(markup).not.toContain("dopełniacz");
    });

    it("holds the asking and failed answers as their own notes", () => {
        expect(cardOf(CHIP, NO_LORE_ANSWER)).toContain("Reading the word");
        expect(cardOf(CHIP, { state: "failed", lore: null, sample: false })).toContain("could not be read");
    });
});
