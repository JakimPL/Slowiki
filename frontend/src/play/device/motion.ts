export type Motion = "system" | "full" | "calm";

const MOTIONS: readonly Motion[] = ["system", "full", "calm"];

export function knownMotion(raw: string | null): Motion | null {
    return MOTIONS.find((candidate) => candidate === raw) ?? null;
}

export function nextMotion(motion: Motion): Motion {
    const index = MOTIONS.indexOf(motion);
    return MOTIONS[(index + 1) % MOTIONS.length] ?? motion;
}

export function appliedMotion(motion: Motion, root: HTMLElement): void {
    if (motion === "system") {
        delete root.dataset.motion;
        return;
    }
    root.dataset.motion = motion;
}
