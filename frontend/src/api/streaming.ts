import type { FetchEventSourceInit } from "@microsoft/fetch-event-source";

import { bodyOf } from "./parsing";
import { gone, reasonOf, refusalOf } from "./refusal";
import type { ClockView, CompanyView, EventView, PositionView } from "./views";

export type Transport = (url: string, init: FetchEventSourceInit) => Promise<void>;

export interface Streamed {
    onOpen: () => void;
    onBeat: () => void;
    onCommit: (event: EventView) => void;
    onPresence: (company: CompanyView) => void;
    onPosition: (view: PositionView) => void;
    onClock: (clock: ClockView) => void;
    onDropped: (reason: string) => void;
    onEnded: () => void;
    onGone: (reason: string) => void;
}

export const PRESENCE_EVENT = "presence";
export const POSITION_EVENT = "position";
export const CLOCK_EVENT = "clock";
export const HEARTBEAT_EVENT = "heartbeat";
export const LAST_EVENT_ID_HEADER = "Last-Event-ID";
export const RETRY_AFTER_DROP_MILLISECONDS = 1000;

export function follow(
    transport: Transport,
    url: string,
    headers: Record<string, string>,
    since: number,
    streamed: Streamed,
): () => void {
    const controller = new AbortController();
    const resumed = since > 0 ? { ...headers, [LAST_EVENT_ID_HEADER]: String(since - 1) } : headers;
    void transport(url, {
        headers: resumed,
        signal: controller.signal,
        openWhenHidden: true,
        onopen: async (response: Response): Promise<void> => {
            if (!response.ok) {
                throw await refusalOf(response);
            }
            streamed.onOpen();
        },
        onmessage: (message): void => {
            streamed.onBeat();
            if (message.event === HEARTBEAT_EVENT) {
                return;
            }
            if (message.event === PRESENCE_EVENT) {
                streamed.onPresence(bodyOf<CompanyView>(message.data));
                return;
            }
            if (message.event === POSITION_EVENT) {
                streamed.onPosition(bodyOf<PositionView>(message.data));
                return;
            }
            if (message.event === CLOCK_EVENT) {
                streamed.onClock(bodyOf<ClockView>(message.data));
                return;
            }
            if (message.data !== "") {
                streamed.onCommit(bodyOf<EventView>(message.data));
            }
        },
        onclose: (): void => {
            streamed.onEnded();
        },
        onerror: (error: unknown): number => {
            if (gone(error)) {
                throw error;
            }
            streamed.onDropped(reasonOf(error));
            return RETRY_AFTER_DROP_MILLISECONDS;
        },
    }).catch((error: unknown) => {
        reported(streamed, error);
    });
    return (): void => {
        controller.abort();
    };
}

function reported(streamed: Streamed, error: unknown): void {
    if (gone(error)) {
        streamed.onGone(reasonOf(error));
        return;
    }
    streamed.onDropped(reasonOf(error));
}
