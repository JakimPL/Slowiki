import type { OfferingsResponse, TableDescription } from "../../api/tables";
import { catalogOf } from "./catalog";
import { deviationsOf } from "./deviation";
import type { Composing } from "./useComposing";

const NOTHING = (): void => undefined;

export interface Inspecting extends Composing {
    readonly scheme: string;
}

export function inspecting(
    arrivals: OfferingsResponse | null,
    description: TableDescription | null,
): Inspecting | null {
    if (arrivals === null || description === null) {
        return null;
    }
    const standard = arrivals.offerings.find((offering) => offering.name === description.scheme)?.rules ?? null;
    if (standard === null) {
        return null;
    }
    const catalog = catalogOf(arrivals.allowances);
    return {
        scheme: description.scheme,
        catalog,
        entries: [],
        entry: null,
        standard,
        record: description.rules,
        deviations: deviationsOf(description.rules, standard, catalog),
        presets: [],
        unsaved: false,
        chooseEntry: NOTHING,
        setSetting: NOTHING,
        revert: NOTHING,
        revertAll: NOTHING,
        savePreset: NOTHING,
        deletePreset: NOTHING,
    };
}
