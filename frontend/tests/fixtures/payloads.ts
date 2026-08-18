import type { StyleTokens, ThemeTokens } from "../../src/api/views";

function aTheme(surface: string): ThemeTokens {
    return {
        chrome: { surface, panel: "#e9e1cd", edge: "#d8cdb2", text: "#2b2419", muted: "#7a6c55" },
        board: {
            surface: "#ede5d1",
            grid: "#d9ceb6",
            frame: "#7a5f44",
            star: "#8f3a24",
            premium_label_share: 0.32,
        },
        premiums: {
            word_2: { fill: "#d8cba8", label: "#6c5b39" },
            word_3: { fill: "#7b6142", label: "#f3ebda" },
        },
        category_premiums: {
            yellow: { fill: "#ebd188", label: "#8a6a14" },
            red: { fill: "#e3b8a8", label: "#8f3a24" },
        },
        tiles: {
            face: "#faf3e1",
            edge: "#cfc3a4",
            text: "#241e14",
            face_tint: 0.15,
            bands: { yellow: "#d9a226", red: "#ac4029" },
        },
        accents: {
            primary: "#7c3f4e",
            on_primary: "#fcf7ec",
            danger: "#9a2f1f",
            success: "#3f7a4b",
            premove: "#6d5e8e",
        },
    };
}

export function aStyle(): StyleTokens {
    return {
        name: "default",
        font_family: "Lato",
        light: aTheme("#f3eddf"),
        dark: aTheme("#211b13"),
    };
}

export function aResponse(status: number, body: unknown): Response {
    return new Response(body === null ? null : JSON.stringify(body), { status });
}
