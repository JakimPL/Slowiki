import "./styles.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import { appliedMode, storedMode } from "./play/mode";

appliedMode(storedMode(window.localStorage), document.documentElement);

const root = document.getElementById("root");
if (root !== null) {
    createRoot(root).render(
        <StrictMode>
            <App />
        </StrictMode>,
    );
}
