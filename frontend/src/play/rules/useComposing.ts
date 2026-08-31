import { useCallback, useMemo, useState } from "react";

import type { OfferingsResponse, RulesConfig, SettingName } from "../../api/tables";
import type { RulesCatalog } from "./catalog";
import { catalogOf, EMPTY_CATALOG } from "./catalog";
import type { RuleChanges, RuleValue } from "./changes";
import { NO_CHANGES, resolvedRules, withoutSetting, withSetting } from "./changes";
import type { Deviation } from "./deviation";
import { deviationsOf } from "./deviation";
import type { RulesEntry } from "./entry";
import { entriesOf, entryOf } from "./entry";
import { EMPTY_BOOK } from "./preset";

export interface Composing {
    readonly catalog: RulesCatalog;
    readonly entries: readonly RulesEntry[];
    readonly entry: RulesEntry | null;
    readonly standard: RulesConfig | null;
    readonly record: RulesConfig | null;
    readonly deviations: readonly Deviation[];
    readonly chooseEntry: (id: string) => void;
    readonly setSetting: (setting: SettingName, value: RuleValue) => void;
    readonly revert: (setting: SettingName) => void;
    readonly revertAll: () => void;
}

export function useComposing(arrivals: OfferingsResponse | null): Composing {
    const [chosen, setChosen] = useState<string | null>(null);
    const [changes, setChanges] = useState<RuleChanges>(NO_CHANGES);

    const catalog = useMemo(() => (arrivals === null ? EMPTY_CATALOG : catalogOf(arrivals.allowances)), [arrivals]);
    const entries = useMemo(() => (arrivals === null ? [] : entriesOf(arrivals.offerings, EMPTY_BOOK)), [arrivals]);
    const entry = entryOf(entries, chosen) ?? entries[0] ?? null;
    const standard = standardOf(arrivals, entry);
    const record = useMemo(
        () => (standard === null ? null : resolvedRules(standard, changes, catalog.settings)),
        [standard, changes, catalog],
    );
    const deviations = useMemo(
        () => (record === null || standard === null ? [] : deviationsOf(record, standard, catalog)),
        [record, standard, catalog],
    );

    const chooseEntry = useCallback(
        (id: string): void => {
            setChosen(id);
            setChanges(entryOf(entries, id)?.changes ?? NO_CHANGES);
        },
        [entries],
    );

    const setSetting = useCallback(
        (setting: SettingName, value: RuleValue): void => {
            if (standard !== null) {
                setChanges((held) => withSetting(held, standard, setting, value));
            }
        },
        [standard],
    );

    const revert = useCallback((setting: SettingName): void => {
        setChanges((held) => withoutSetting(held, setting));
    }, []);

    const revertAll = useCallback((): void => {
        setChanges(NO_CHANGES);
    }, []);

    return {
        catalog,
        entries,
        entry,
        standard,
        record,
        deviations,
        chooseEntry,
        setSetting,
        revert,
        revertAll,
    };
}

function standardOf(arrivals: OfferingsResponse | null, entry: RulesEntry | null): RulesConfig | null {
    if (arrivals === null || entry === null) {
        return null;
    }
    return arrivals.offerings.find((offering) => offering.name === entry.origin)?.rules ?? null;
}
