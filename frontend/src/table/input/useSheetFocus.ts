import type { RefObject } from "react";
import { useEffect, useRef } from "react";

export function useSheetFocus<Held extends HTMLElement>(): RefObject<Held | null> {
    const sheet = useRef<Held | null>(null);
    useEffect(() => {
        const opener = document.activeElement;
        sheet.current?.focus();
        return (): void => {
            if (opener instanceof HTMLElement) {
                opener.focus();
            }
        };
    }, []);
    return sheet;
}
