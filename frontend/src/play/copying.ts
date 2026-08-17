const OFFSCREEN_TOP = "-1000px";
const CLIPBOARD_WAIT_MS = 400;

export async function copiedText(text: string): Promise<boolean> {
    if (window.isSecureContext && (await writtenToClipboard(text))) {
        return true;
    }
    return copiedThroughSelection(text);
}

function writtenToClipboard(text: string): Promise<boolean> {
    const written = navigator.clipboard.writeText(text).then(
        () => true,
        () => false,
    );
    const waited = new Promise<boolean>((settle) => {
        window.setTimeout(() => {
            settle(false);
        }, CLIPBOARD_WAIT_MS);
    });
    return Promise.race([written, waited]);
}

function copiedThroughSelection(text: string): boolean {
    const holder = document.createElement("textarea");
    holder.value = text;
    holder.style.position = "fixed";
    holder.style.top = OFFSCREEN_TOP;
    document.body.append(holder);
    holder.focus({ preventScroll: true });
    holder.setSelectionRange(0, text.length);
    // eslint-disable-next-line @typescript-eslint/no-deprecated
    const copied = document.execCommand("copy");
    holder.remove();
    return copied;
}
