export const NAME_STORAGE_KEY = "literabble-name";

export function storedName(storage: Pick<Storage, "getItem">): string {
    return storage.getItem(NAME_STORAGE_KEY) ?? "";
}

export function rememberName(name: string | null, storage: Pick<Storage, "setItem" | "removeItem">): void {
    if (name === null) {
        storage.removeItem(NAME_STORAGE_KEY);
        return;
    }
    storage.setItem(NAME_STORAGE_KEY, name);
}
