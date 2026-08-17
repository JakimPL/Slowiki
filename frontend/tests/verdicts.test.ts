import { describe, expect, it } from "vitest";

import { NO_JUDGEMENTS, unjudged, withVerdicts } from "../src/play/verdicts";

describe("verdicts", () => {
    it("asks once for every word still unknown", () => {
        expect(unjudged(["DOM", "DOM", "OSA", ""], NO_JUDGEMENTS)).toEqual(["DOM", "OSA"]);
        expect(unjudged(["DOM", "OSA"], new Map([["DOM", true]]))).toEqual(["OSA"]);
        expect(unjudged(["DOM"], new Map([["DOM", false]]))).toEqual([]);
    });

    it("keeps the answers the dictionary already gave", () => {
        const judged = withVerdicts(NO_JUDGEMENTS, {
            DOM: { allowed: true, reason: null },
            KOTZ: { allowed: false, reason: "unknown word" },
        });
        expect(judged.get("DOM")).toBe(true);
        expect(judged.get("KOTZ")).toBe(false);
        const later = withVerdicts(judged, { OSA: { allowed: true, reason: null } });
        expect([...later.keys()]).toEqual(["DOM", "KOTZ", "OSA"]);
    });
});
