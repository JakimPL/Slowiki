import type { ReactElement } from "react";
import { useEffect, useState } from "react";

import { readStyle } from "./api/client";
import { PRODUCT_NAME, PRODUCT_TAGLINE, SHELL_NOTE, STYLE_FALLBACK_NOTE } from "./table/strings";
import { applyTheme } from "./table/theme";

type ThemeSource = "loading" | "server" | "fallback";

const SPECIMEN_TILES: readonly { letter: string; category: string }[] = [
    { letter: "S", category: "yellow" },
    { letter: "Ł", category: "blue" },
    { letter: "O", category: "yellow" },
    { letter: "W", category: "yellow" },
    { letter: "A", category: "yellow" },
];

export function App(): ReactElement {
    const [themeSource, setThemeSource] = useState<ThemeSource>("loading");

    useEffect(() => {
        let mounted = true;
        readStyle()
            .then((style) => {
                applyTheme(style, document);
                if (mounted) {
                    setThemeSource("server");
                }
            })
            .catch(() => {
                if (mounted) {
                    setThemeSource("fallback");
                }
            });
        return (): void => {
            mounted = false;
        };
    }, []);

    return (
        <main className="shell">
            <div className="specimen" aria-hidden="true">
                {SPECIMEN_TILES.map((tile, position) => (
                    <b key={position} data-category={tile.category}>
                        {tile.letter}
                    </b>
                ))}
            </div>
            <h1>{PRODUCT_NAME}</h1>
            <p className="tagline">{PRODUCT_TAGLINE}</p>
            <p className="note">{themeSource === "fallback" ? STYLE_FALLBACK_NOTE : SHELL_NOTE}</p>
        </main>
    );
}
