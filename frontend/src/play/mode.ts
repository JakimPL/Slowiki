export type Mode = "system" | "light" | "dark";

export const MODE_STORAGE_KEY = "literabble-mode";

const CYCLE: readonly Mode[] = ["system", "light", "dark"];

export function storedMode(storage: Pick<Storage, "getItem">): Mode {
    const raw = storage.getItem(MODE_STORAGE_KEY);
    return raw === "light" || raw === "dark" ? raw : "system";
}

export function nextMode(mode: Mode): Mode {
    const index = CYCLE.indexOf(mode);
    return CYCLE[(index + 1) % CYCLE.length] ?? "system";
}

export function rememberMode(mode: Mode, storage: Pick<Storage, "setItem" | "removeItem">): void {
    if (mode === "system") {
        storage.removeItem(MODE_STORAGE_KEY);
        return;
    }
    storage.setItem(MODE_STORAGE_KEY, mode);
}

export function appliedMode(mode: Mode, root: HTMLElement): void {
    if (mode === "system") {
        delete root.dataset.mode;
        return;
    }
    root.dataset.mode = mode;
}
