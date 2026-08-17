import { fetchEventSource } from "@microsoft/fetch-event-source";

import type { Move, MoveAccepted, MoveRequest } from "./moves";
import { parsed } from "./parsing";
import { refusalOf } from "./refusal";
import type { Seat } from "./seat";
import { headersFor } from "./seat";
import type { Streamed } from "./streaming";
import { follow } from "./streaming";
import type {
    JoinRequest,
    Offering,
    OfferingsResponse,
    TableAdmission,
    TableDescription,
    TableRequest,
} from "./tables";
import type { StyleTokens, TableViewResponse } from "./views";

const JSON_HEADERS: Record<string, string> = { "Content-Type": "application/json" };

async function answered(response: Response): Promise<Response> {
    if (!response.ok) {
        throw await refusalOf(response);
    }
    return response;
}

export async function readOfferings(): Promise<readonly Offering[]> {
    const response = await answered(await fetch("/offerings"));
    const body = await parsed<OfferingsResponse>(response);
    return body.offerings;
}

export async function readStyle(): Promise<StyleTokens> {
    const response = await answered(await fetch("/style"));
    return parsed<StyleTokens>(response);
}

export async function createTable(request: TableRequest): Promise<TableAdmission> {
    const response = await answered(
        await fetch("/tables", {
            method: "POST",
            headers: JSON_HEADERS,
            body: JSON.stringify(request),
        }),
    );
    return parsed<TableAdmission>(response);
}

export async function joinTable(code: string, request: JoinRequest): Promise<TableAdmission> {
    const response = await answered(
        await fetch(`/tables/${encodeURIComponent(code)}/join`, {
            method: "POST",
            headers: JSON_HEADERS,
            body: JSON.stringify(request),
        }),
    );
    return parsed<TableAdmission>(response);
}

export async function readDescription(seat: Seat): Promise<TableDescription> {
    const response = await answered(
        await fetch(`/tables/${encodeURIComponent(seat.table)}`, { headers: headersFor(seat) }),
    );
    return parsed<TableDescription>(response);
}

export async function readView(seat: Seat): Promise<TableViewResponse> {
    const response = await answered(
        await fetch(`/tables/${encodeURIComponent(seat.table)}/view`, { headers: headersFor(seat) }),
    );
    return parsed<TableViewResponse>(response);
}

export async function sendMove(seat: Seat, move: Move, baseSeq: number, premove: boolean): Promise<number> {
    const request: MoveRequest = { move, base_seq: baseSeq, premove };
    const response = await answered(
        await fetch(`/tables/${encodeURIComponent(seat.table)}/moves`, {
            method: "POST",
            headers: { ...JSON_HEADERS, ...headersFor(seat) },
            body: JSON.stringify(request),
        }),
    );
    const body = await parsed<MoveAccepted>(response);
    return body.seq;
}

export async function cancelPremove(seat: Seat, baseSeq: number): Promise<number> {
    const response = await answered(
        await fetch(`/tables/${encodeURIComponent(seat.table)}/premove?base_seq=${String(baseSeq)}`, {
            method: "DELETE",
            headers: headersFor(seat),
        }),
    );
    const body = await parsed<MoveAccepted>(response);
    return body.seq;
}

export function followEvents(seat: Seat, since: number, streamed: Streamed): () => void {
    const url = `/tables/${encodeURIComponent(seat.table)}/events`;
    return follow(fetchEventSource, url, headersFor(seat), since, streamed);
}
