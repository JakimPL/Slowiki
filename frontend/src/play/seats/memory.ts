import { standingIn } from "./session";

export const SEAT_STORAGE_KEY = "slowiki-seat";

export function storedSeat(storage: Pick<Storage, "getItem">): string | null {
    const held = storage.getItem(SEAT_STORAGE_KEY);
    if (held === null) {
        return null;
    }
    const standing = standingIn(held);
    return standing.table !== null && standing.token !== null ? held : null;
}

export function rememberSeat(fragment: string, storage: Pick<Storage, "setItem">): void {
    storage.setItem(SEAT_STORAGE_KEY, fragment);
}

export function forgetSeat(storage: Pick<Storage, "removeItem">): void {
    storage.removeItem(SEAT_STORAGE_KEY);
}
