export interface Tint {
    readonly name: string;
    readonly hex: string;
}

const ROSE: Tint = { name: "rose", hex: "#C95B79" };

export const PLAYER_TINTS: readonly Tint[] = [
    ROSE,
    { name: "coral", hex: "#D07A4F" },
    { name: "copper", hex: "#A8703D" },
    { name: "teal", hex: "#2FA08C" },
    { name: "azure", hex: "#3FA3CF" },
    { name: "indigo", hex: "#5668C9" },
    { name: "violet", hex: "#8A5BB8" },
    { name: "graphite", hex: "#6E7B8A" },
];

export function tintFor(seat: number): Tint {
    return PLAYER_TINTS[seat % PLAYER_TINTS.length] ?? ROSE;
}
