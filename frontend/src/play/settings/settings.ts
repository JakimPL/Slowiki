import type { Locale } from "../../text/keys";
import type { Mode } from "../device/mode";
import type { Motion } from "../device/motion";

export interface Settings {
    readonly mode: Mode;
    readonly motion: Motion;
    readonly locale: Locale | null;
    readonly notices: boolean;
}

export const DEFAULT_SETTINGS: Settings = {
    mode: "system",
    motion: "system",
    locale: null,
    notices: false,
};
