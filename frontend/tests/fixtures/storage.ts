export interface FakeStorage extends Storage {
    readonly entries: Map<string, string>;
}

export function aStorage(initial: Record<string, string> = {}): FakeStorage {
    const entries = new Map(Object.entries(initial));
    return {
        entries,
        get length(): number {
            return entries.size;
        },
        clear: (): void => {
            entries.clear();
        },
        key: (index: number): string | null => [...entries.keys()][index] ?? null,
        getItem: (key: string): string | null => entries.get(key) ?? null,
        setItem: (key: string, value: string): void => {
            entries.set(key, value);
        },
        removeItem: (key: string): void => {
            entries.delete(key);
        },
    };
}
