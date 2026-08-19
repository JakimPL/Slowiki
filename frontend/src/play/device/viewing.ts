export interface Watched {
    readonly visibilityState: DocumentVisibilityState;
    addEventListener(type: "visibilitychange", listener: () => void): void;
    removeEventListener(type: "visibilitychange", listener: () => void): void;
}

export function whileInView(watched: Watched, hold: () => () => void): () => void {
    let release: (() => void) | null = null;
    const settle = (): void => {
        if (watched.visibilityState === "visible") {
            release = release ?? hold();
            return;
        }
        if (release !== null) {
            release();
            release = null;
        }
    };
    watched.addEventListener("visibilitychange", settle);
    settle();
    return (): void => {
        watched.removeEventListener("visibilitychange", settle);
        if (release !== null) {
            release();
            release = null;
        }
    };
}
