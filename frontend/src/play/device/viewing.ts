export interface Watched {
    readonly visibilityState: DocumentVisibilityState;
    addEventListener(type: "visibilitychange", listener: () => void): void;
    removeEventListener(type: "visibilitychange", listener: () => void): void;
}

export function whenInView(watched: Watched, returned: () => void): () => void {
    const settle = (): void => {
        if (watched.visibilityState === "visible") {
            returned();
        }
    };
    watched.addEventListener("visibilitychange", settle);
    return (): void => {
        watched.removeEventListener("visibilitychange", settle);
    };
}
