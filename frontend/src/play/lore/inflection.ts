import type { Inflection } from "../../api/lore";
import type { Dimension } from "./tagset";
import { DIMENSION_ORDER, termsOn } from "./tagset";

export function inflectionTerms(tags: Inflection, except: readonly Dimension[]): readonly string[] {
    const covered = new Set(except);
    return DIMENSION_ORDER.filter((dimension) => !covered.has(dimension)).flatMap((dimension) =>
        termsOn(tags, dimension),
    );
}
