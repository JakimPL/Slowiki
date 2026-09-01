export function typedValue(typed: string, minimum: number, maximum: number): number | null {
    const asked = Number(typed.trim());
    if (typed.trim() === "" || !Number.isFinite(asked)) {
        return null;
    }
    return Math.min(maximum, Math.max(minimum, Math.round(asked)));
}
