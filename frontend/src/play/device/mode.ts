export type Mode = "system" | "light" | "dark";

export const MODES: readonly Mode[] = ["system", "light", "dark"];

export function knownMode(raw: string | null): Mode | null {
    return MODES.find((candidate) => candidate === raw) ?? null;
}

export function nextMode(mode: Mode): Mode {
    const index = MODES.indexOf(mode);
    return MODES[(index + 1) % MODES.length] ?? mode;
}

export function appliedMode(mode: Mode, root: HTMLElement): void {
    if (mode === "system") {
        delete root.dataset.mode;
        return;
    }
    root.dataset.mode = mode;
}
