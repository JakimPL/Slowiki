import type { TouchEvent as ReactTouchEvent } from "react";
import { useEffect, useRef, useState } from "react";

export const HOLD_MILLISECONDS = 450;

export interface HoldBinding {
    readonly held: number | null;
    readonly press: (cell: number) => void;
    readonly release: () => void;
    readonly consumed: (event: ReactTouchEvent<HTMLElement>) => void;
}

export function useHold(onHold: ((cell: number) => void) | null): HoldBinding | null {
    const [held, setHeld] = useState<number | null>(null);
    const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const opened = useRef(false);
    useEffect(
        () => (): void => {
            if (timer.current !== null) {
                clearTimeout(timer.current);
            }
        },
        [],
    );
    if (onHold === null) {
        return null;
    }
    const stop = (): void => {
        if (timer.current !== null) {
            clearTimeout(timer.current);
            timer.current = null;
        }
        setHeld(null);
    };
    return {
        held,
        press: (cell: number): void => {
            stop();
            opened.current = false;
            setHeld(cell);
            timer.current = setTimeout(() => {
                stop();
                opened.current = true;
                onHold(cell);
            }, HOLD_MILLISECONDS);
        },
        release: stop,
        consumed: (event: ReactTouchEvent<HTMLElement>): void => {
            if (opened.current) {
                event.preventDefault();
                opened.current = false;
            }
        },
    };
}
