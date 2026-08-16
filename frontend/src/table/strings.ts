import type { Connection } from "../play/connection";

export const PRODUCT_NAME = "Literabble";
export const PRODUCT_TAGLINE = "A configurable Literaki and Scrabble table.";
export const SHELL_NOTE = "The redesigned table screens arrive with the next build step.";
export const STYLE_FALLBACK_NOTE = "Server style unavailable — showing the built-in palette.";

export const CONNECTION_CAPTIONS: Record<Connection, string> = {
    joining: "Joining",
    live: "Live",
    resuming: "Reconnecting",
    lost: "Disconnected",
};
