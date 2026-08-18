export interface KeyHandlers {
    readonly onEscape: () => void;
    readonly onEnter: () => void;
}

export function boundKeys(target: Document, handlers: KeyHandlers): () => void {
    const listen = (event: KeyboardEvent): void => {
        if (event.key === "Escape") {
            handlers.onEscape();
            return;
        }
        if (event.key === "Enter" && !typing(event)) {
            handlers.onEnter();
        }
    };
    target.addEventListener("keydown", listen);
    return (): void => {
        target.removeEventListener("keydown", listen);
    };
}

function typing(event: KeyboardEvent): boolean {
    return event.target instanceof HTMLElement && event.target.closest("input, textarea, select, button") !== null;
}
