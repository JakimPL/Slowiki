import "./styles.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import { appliedLocale } from "./play/device/locale";
import { appliedMode, storedMode } from "./play/device/mode";
import { activeLocale } from "./text/active";

appliedMode(storedMode(window.localStorage), document.documentElement);
appliedLocale(activeLocale(), document.documentElement);

const root = document.getElementById("root");
if (root !== null) {
    createRoot(root).render(
        <StrictMode>
            <App />
        </StrictMode>,
    );
}
