import { describe, expect, it } from "vitest";

import type { Pending } from "../src/play/draft";
import {
    draftedIdentifiers,
    EMPTY_DRAFT,
    laidDown,
    laidOf,
    pendingAt,
    placementsOf,
    reconciledDraft,
    shownTile,
    stamped,
    takenBack,
} from "../src/play/draft";
import { aBoard, aTile } from "./positions";

const KAY: Pending = { cell: 112, tile: aTile({ identifier: 7, letter: "K" }), letter: null };
const BLANK: Pending = { cell: 113, tile: aTile({ identifier: 8, letter: "", blank: true }), letter: "Ż" };

describe("draft", () => {
    it("lays tiles onto free cells only", () => {
        const draft = laidDown(laidDown(EMPTY_DRAFT, KAY), { ...BLANK, cell: 112 });
        expect(draft).toEqual([KAY]);
        expect(pendingAt(draft, 112)).toEqual(KAY);
        expect(pendingAt(draft, 113)).toBeNull();
    });

    it("takes a pending tile back", () => {
        const draft = takenBack(laidDown(EMPTY_DRAFT, KAY), 112);
        expect(draft).toEqual([]);
    });

    it("tracks drafted identifiers", () => {
        const draft = laidDown(laidDown(EMPTY_DRAFT, KAY), BLANK);
        expect(draftedIdentifiers(draft)).toEqual(new Set([7, 8]));
    });

    it("shows the assigned letter on a laid blank", () => {
        expect(shownTile(BLANK).letter).toBe("Ż");
        expect(shownTile(KAY)).toEqual(KAY.tile);
        expect(laidOf([BLANK])[0]?.tile.letter).toBe("Ż");
    });

    it("stamps the chosen letter onto the hanging blank", () => {
        const hanging: Pending = { ...BLANK, letter: null };
        const draft = laidDown(laidDown(EMPTY_DRAFT, KAY), hanging);
        expect(shownTile(hanging).letter).toBe("");
        expect(stamped(draft, 113, "Ż")).toEqual([KAY, BLANK]);
        expect(stamped(draft, 111, "Ż")).toEqual(draft);
    });

    it("builds wire placements with rows, columns, and blank letters", () => {
        expect(placementsOf([KAY, BLANK], 15)).toEqual([
            { tile_id: 7, row: 7, column: 7, letter: null },
            { tile_id: 8, row: 7, column: 8, letter: "Ż" },
        ]);
    });

    it("keeps pending tiles while they stay in the rack and the cell stays free", () => {
        const draft = laidDown(laidDown(EMPTY_DRAFT, KAY), BLANK);
        const rack = [KAY.tile, BLANK.tile];
        const free = new Set<number>();
        expect(reconciledDraft(draft, rack, aBoard(), free)).toBe(draft);
        expect(reconciledDraft(draft, [KAY.tile], aBoard(), free)).toEqual([KAY]);
        expect(reconciledDraft(draft, rack, aBoard({ 112: aTile() }), free)).toEqual([BLANK]);
        expect(reconciledDraft(draft, null, aBoard(), free)).toEqual([]);
    });

    it("hands committed tiles over to the premove mirror", () => {
        const draft = laidDown(laidDown(EMPTY_DRAFT, KAY), BLANK);
        const rack = [KAY.tile, BLANK.tile];
        expect(reconciledDraft(draft, rack, aBoard(), new Set([KAY.tile.identifier]))).toEqual([BLANK]);
    });
});
