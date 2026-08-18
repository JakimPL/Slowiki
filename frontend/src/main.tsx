import "./styles.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import { appliedLocale } from "./play/device/locale";
import { appliedMode } from "./play/device/mode";
import { appliedMotion } from "./play/device/motion";
import { currentSettings } from "./play/settings/storage";
import { SettingsProvider } from "./play/settings/useSettings";
import { activeLocale } from "./text/active";

const settings = currentSettings();
appliedMode(settings.mode, document.documentElement);
appliedMotion(settings.motion, document.documentElement);
appliedLocale(activeLocale(), document.documentElement);

const root = document.getElementById("root");
if (root !== null) {
    createRoot(root).render(
        <StrictMode>
            <SettingsProvider>
                <App />
            </SettingsProvider>
        </StrictMode>,
    );
}
