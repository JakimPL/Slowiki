import { useCallback, useEffect, useMemo, useState } from "react";

import type { OfferingsResponse, RulesConfig, SettingName } from "../../api/tables";
import type { RulesCatalog } from "./catalog";
import { catalogOf, EMPTY_CATALOG } from "./catalog";
import type { RuleChanges, RuleValue } from "./changes";
import { NO_CHANGES, resolvedRules, sameValue, withoutSetting, withSetting } from "./changes";
import type { Deviation } from "./deviation";
import { deviationsOf } from "./deviation";
import type { RulesEntry } from "./entry";
import { entriesOf, entryOf } from "./entry";
import type { PresetBook, SavedPreset } from "./preset";
import { EMPTY_BOOK, lastUsed, presetOf, withoutPreset, withPreset } from "./preset";
import { newPresetId, rememberPresets, storedPresets } from "./storage";

export interface Composing {
    readonly catalog: RulesCatalog;
    readonly entries: readonly RulesEntry[];
    readonly entry: RulesEntry | null;
    readonly standard: RulesConfig | null;
    readonly record: RulesConfig | null;
    readonly deviations: readonly Deviation[];
    readonly presets: readonly SavedPreset[];
    readonly unsaved: boolean;
    readonly chooseEntry: (id: string) => void;
    readonly setSetting: (setting: SettingName, value: RuleValue) => void;
    readonly revert: (setting: SettingName) => void;
    readonly revertAll: () => void;
    readonly savePreset: (label: string) => void;
    readonly deletePreset: (id: string) => void;
}

export function useComposing(arrivals: OfferingsResponse | null): Composing {
    const [book, setBook] = useState<PresetBook>(currentBook);
    const [chosen, setChosen] = useState<string | null>(book.last);
    const [changes, setChanges] = useState<RuleChanges>(() => presetOf(book, book.last)?.changes ?? NO_CHANGES);

    const catalog = useMemo(() => (arrivals === null ? EMPTY_CATALOG : catalogOf(arrivals.allowances)), [arrivals]);
    const entries = useMemo(() => (arrivals === null ? [] : entriesOf(arrivals.offerings, book)), [arrivals, book]);
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

    useEffect(() => {
        if (typeof window !== "undefined") {
            rememberPresets(book, window.localStorage);
        }
    }, [book]);

    const chooseEntry = useCallback(
        (id: string): void => {
            setChosen(id);
            setChanges(entryOf(entries, id)?.changes ?? NO_CHANGES);
            setBook((held) => lastUsed(held, id));
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

    const savePreset = useCallback(
        (label: string): void => {
            if (entry === null) {
                return;
            }
            const saved: SavedPreset = {
                id: entry.saved ? entry.id : newPresetId(),
                label,
                origin: entry.origin,
                changes,
                saved: Date.now(),
            };
            setBook((held) => withPreset(held, saved));
            setChosen(saved.id);
        },
        [entry, changes],
    );

    const deletePreset = useCallback((id: string): void => {
        setBook((held) => withoutPreset(held, id));
        setChosen(null);
        setChanges(NO_CHANGES);
    }, []);

    return {
        catalog,
        entries,
        entry,
        standard,
        record,
        deviations,
        presets: book.presets,
        unsaved: unsavedAgainst(entry, changes, catalog),
        chooseEntry,
        setSetting,
        revert,
        revertAll,
        savePreset,
        deletePreset,
    };
}

function currentBook(): PresetBook {
    return typeof window === "undefined" ? EMPTY_BOOK : storedPresets(window.localStorage);
}

function unsavedAgainst(entry: RulesEntry | null, changes: RuleChanges, catalog: RulesCatalog): boolean {
    if (entry === null) {
        return false;
    }
    return catalog.settings.some((setting) => !sameValue(changes[setting] ?? null, entry.changes[setting] ?? null));
}

function standardOf(arrivals: OfferingsResponse | null, entry: RulesEntry | null): RulesConfig | null {
    if (arrivals === null || entry === null) {
        return null;
    }
    return arrivals.offerings.find((offering) => offering.name === entry.origin)?.rules ?? null;
}
