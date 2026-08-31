import { fetchEventSource } from "@microsoft/fetch-event-source";

import type { GameHighlights } from "./highlights";
import type { WordLoreResponse } from "./lore";
import type { Move, MoveAccepted, MoveRequest } from "./moves";
import { parsed } from "./parsing";
import type { RackRequest } from "./rack";
import { refusalOf } from "./refusal";
import type { Seat } from "./seat";
import { headersFor } from "./seat";
import type { Streamed } from "./streaming";
import { follow } from "./streaming";
import type {
    JoinRequest,
    OfferingsResponse,
    PresetsResponse,
    TableAdmission,
    TableDescription,
    TableRequest,
} from "./tables";
import type { StyleTokens, TableViewResponse } from "./views";
import type { WordVerdicts } from "./words";

const JSON_HEADERS: Record<string, string> = { "Content-Type": "application/json" };

async function answered(response: Response): Promise<Response> {
    if (!response.ok) {
        throw await refusalOf(response);
    }
    return response;
}

export async function readOfferings(): Promise<OfferingsResponse> {
    const response = await answered(await fetch("/offerings"));
    return parsed<OfferingsResponse>(response);
}

export async function readInvitation(code: string): Promise<TableDescription> {
    const response = await answered(await fetch(`/invitations/${encodeURIComponent(code)}`));
    return parsed<TableDescription>(response);
}

export async function readPresets(): Promise<PresetsResponse> {
    const response = await answered(await fetch("/presets"));
    return parsed<PresetsResponse>(response);
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

async function askedAbout(seat: Seat, route: string, words: readonly string[]): Promise<Response> {
    const asked = words.map((word) => `words=${encodeURIComponent(word)}`).join("&");
    return answered(
        await fetch(`/tables/${encodeURIComponent(seat.table)}/${route}?${asked}`, { headers: headersFor(seat) }),
    );
}

export async function readWordVerdicts(seat: Seat, words: readonly string[]): Promise<WordVerdicts> {
    return parsed<WordVerdicts>(await askedAbout(seat, "words", words));
}

export async function readWordLore(seat: Seat, words: readonly string[]): Promise<WordLoreResponse> {
    return parsed<WordLoreResponse>(await askedAbout(seat, "lore", words));
}

export async function readHighlights(seat: Seat): Promise<GameHighlights> {
    const response = await answered(
        await fetch(`/tables/${encodeURIComponent(seat.table)}/highlights`, { headers: headersFor(seat) }),
    );
    return parsed<GameHighlights>(response);
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

export async function sendRackOrder(seat: Seat, tileIdentifiers: readonly number[]): Promise<void> {
    const request: RackRequest = { tile_ids: [...tileIdentifiers] };
    await answered(
        await fetch(`/tables/${encodeURIComponent(seat.table)}/rack`, {
            method: "PUT",
            headers: { ...JSON_HEADERS, ...headersFor(seat) },
            body: JSON.stringify(request),
        }),
    );
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
