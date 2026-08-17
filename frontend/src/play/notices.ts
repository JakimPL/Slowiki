export const NOTICE_STORAGE_KEY = "literabble-notices";
export const NOTICE_TAG = "literabble-turn";

const WANTED_VALUE = "on";
const GRANTED = "granted";

export function storedNotices(storage: Pick<Storage, "getItem">): boolean {
    return storage.getItem(NOTICE_STORAGE_KEY) === WANTED_VALUE;
}

export function rememberNotices(wanted: boolean, storage: Pick<Storage, "setItem" | "removeItem">): void {
    if (wanted) {
        storage.setItem(NOTICE_STORAGE_KEY, WANTED_VALUE);
        return;
    }
    storage.removeItem(NOTICE_STORAGE_KEY);
}

export function noticeDue(wanted: boolean, acting: boolean, hidden: boolean, permission: string): boolean {
    return wanted && acting && hidden && permission === GRANTED;
}

export async function requestedNotices(): Promise<boolean> {
    if (typeof Notification === "undefined") {
        return false;
    }
    const answer = await Notification.requestPermission();
    return answer === GRANTED;
}

export function grantedNotices(): string {
    return typeof Notification === "undefined" ? "unsupported" : Notification.permission;
}

export function announced(title: string, body: string): void {
    if (typeof Notification === "undefined") {
        return;
    }
    const posted = new Notification(title, { body, tag: NOTICE_TAG });
    posted.onclick = (): void => {
        window.focus();
        posted.close();
    };
}
