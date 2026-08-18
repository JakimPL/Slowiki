import type { ReactElement, ReactNode } from "react";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { appliedMode } from "../device/mode";
import { appliedMotion } from "../device/motion";
import type { Settings } from "./settings";
import { currentSettings, rememberSettings } from "./storage";

export interface SettingsHold {
    readonly settings: Settings;
    readonly change: (patch: Partial<Settings>) => void;
}

export interface SettingsProviderProps {
    readonly children: ReactNode;
}

const HELD = createContext<SettingsHold | null>(null);

export function SettingsProvider({ children }: SettingsProviderProps): ReactElement {
    const [settings, setSettings] = useState<Settings>(currentSettings);

    const change = useCallback(
        (patch: Partial<Settings>): void => {
            const upcoming = { ...settings, ...patch };
            rememberSettings(upcoming, window.localStorage);
            setSettings(upcoming);
        },
        [settings],
    );

    useEffect(() => {
        appliedMode(settings.mode, document.documentElement);
        appliedMotion(settings.motion, document.documentElement);
    }, [settings.mode, settings.motion]);

    const held = useMemo((): SettingsHold => ({ settings, change }), [settings, change]);
    return <HELD.Provider value={held}>{children}</HELD.Provider>;
}

export function useSettings(): SettingsHold {
    const held = useContext(HELD);
    if (held === null) {
        throw new Error("settings are read inside the settings provider");
    }
    return held;
}
