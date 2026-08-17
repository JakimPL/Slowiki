import type { StyleTokens, ThemeTokens } from "../api/views";
import { mixHex } from "./color";

export const THEME_STYLE_ELEMENT_ID = "theme-tokens";

export function cssFor(style: StyleTokens): string {
    const light = declarationsFor(style.light).join("\n    ");
    const dark = declarationsFor(style.dark).join("\n    ");
    return [
        `:root {\n    ${light}\n}`,
        `@media (prefers-color-scheme: dark) {\n:root:not([data-mode="light"]) {\n    ${dark}\n}\n}`,
        `:root[data-mode="dark"] {\n    ${dark}\n}`,
        "",
    ].join("\n");
}

export function declarationsFor(theme: ThemeTokens): readonly string[] {
    const declarations: string[] = [
        `--chrome-surface: ${theme.chrome.surface};`,
        `--chrome-panel: ${theme.chrome.panel};`,
        `--chrome-edge: ${theme.chrome.edge};`,
        `--chrome-text: ${theme.chrome.text};`,
        `--chrome-muted: ${theme.chrome.muted};`,
        `--board-surface: ${theme.board.surface};`,
        `--board-grid: ${theme.board.grid};`,
        `--board-frame: ${theme.board.frame};`,
        `--board-star: ${theme.board.star};`,
        `--tile-face: ${theme.tiles.face};`,
        `--tile-edge: ${theme.tiles.edge};`,
        `--tile-text: ${theme.tiles.text};`,
        `--accent-primary: ${theme.accents.primary};`,
        `--accent-on-primary: ${theme.accents.on_primary};`,
        `--accent-danger: ${theme.accents.danger};`,
        `--accent-success: ${theme.accents.success};`,
        `--accent-premove: ${theme.accents.premove};`,
    ];
    for (const [name, premium] of Object.entries(theme.premiums)) {
        declarations.push(`--premium-${slugOf(name)}-fill: ${premium.fill};`);
        declarations.push(`--premium-${slugOf(name)}-label: ${premium.label};`);
    }
    for (const [category, premium] of Object.entries(theme.category_premiums)) {
        declarations.push(`--category-${slugOf(category)}-fill: ${premium.fill};`);
        declarations.push(`--category-${slugOf(category)}-label: ${premium.label};`);
    }
    for (const [category, band] of Object.entries(theme.tiles.bands)) {
        declarations.push(`--band-${slugOf(category)}: ${band};`);
        declarations.push(`--tile-face-${slugOf(category)}: ${mixHex(theme.tiles.face, band, theme.tiles.face_tint)};`);
    }
    return declarations;
}

export function applyTheme(style: StyleTokens, target: Document): void {
    const existing = target.getElementById(THEME_STYLE_ELEMENT_ID);
    const holder = existing ?? target.createElement("style");
    holder.id = THEME_STYLE_ELEMENT_ID;
    holder.textContent = cssFor(style);
    if (existing === null) {
        target.head.appendChild(holder);
    }
}

export function slugOf(name: string): string {
    return name.replaceAll("_", "-");
}
