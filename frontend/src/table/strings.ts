import type { CompanyView } from "../api/views";
import type { Connection } from "../play/connection";
import type { Story } from "../play/story";

export const PRODUCT_NAME = "Literabble";
export const PRODUCT_TAGLINE = "A configurable Literaki and Scrabble table.";
export const STYLE_FALLBACK_NOTE = "Server style unavailable — showing the built-in palette.";

export const CONNECTION_CAPTIONS: Record<Connection, string> = {
    joining: "Joining",
    live: "Live",
    resuming: "Reconnecting",
    lost: "Disconnected",
};

export const NAME_LABEL = "Your name";
export const NAME_PLACEHOLDER = "Shown on your plaque";
export const CREATE_HEADING = "Start a table";
export const JOIN_HEADING = "Join a table";
export const SCHEME_LABEL = "Game";
export const SEATS_LABEL = "Players";
export const CODE_LABEL = "Table code";
export const CREATE_BUTTON = "Start the table";
export const JOIN_BUTTON = "Join the table";
export const JOINING_CAPTION = "Joining the table…";
export const OFFERINGS_LOADING = "Reading the table offerings…";
export const OPEN_SEAT_LABEL = "Open seat";
export const YOU_MARKER = "you";
export const YOUR_TURN_CAPTION = "Your turn";
export const GAME_OVER_HEADING = "Game over";
export const INVITE_BUTTON = "Copy invitation";
export const INVITE_COPIED = "Invitation copied";
export const BOARD_LABEL = "Board";
export const RACK_LABEL = "Your tiles";

export function fallbackNameFor(seat: number): string {
    return `Player ${String(seat + 1)}`;
}

export function nameFor(company: CompanyView, seat: number): string {
    const seated = company.seats.find((candidate) => candidate.seat === seat);
    if (seated?.claimed !== true) {
        return OPEN_SEAT_LABEL;
    }
    return seated.name ?? fallbackNameFor(seat);
}

export function bagCaption(count: number): string {
    return `Bag ${String(count)}`;
}

export function offeringCaption(name: string, minimum: number, maximum: number): string {
    const span = minimum === maximum ? String(minimum) : `${String(minimum)}–${String(maximum)}`;
    return `${name} · ${span} ${maximum === 1 ? "player" : "players"}`;
}

export function gatheringCaption(present: number, total: number): string {
    return `Gathering players — ${String(present)} of ${String(total)} at the table`;
}

export function thinkingCaption(names: readonly string[]): string {
    if (names.length === 0) {
        return "Waiting…";
    }
    return `${listed(names)} ${names.length === 1 ? "is" : "are"} thinking…`;
}

export function wonCaption(names: readonly string[], points: number): string {
    if (names.length === 1) {
        return `${names[0] ?? ""} wins with ${String(points)}`;
    }
    return `${listed(names)} share the win with ${String(points)}`;
}

export function captionFor(story: Story, company: CompanyView): string {
    switch (story.kind) {
        case "acting":
            return YOUR_TURN_CAPTION;
        case "gathering": {
            const present = company.seats.filter((seated) => seated.claimed).length;
            return gatheringCaption(present, company.seats.length);
        }
        case "over":
            return wonCaption(
                story.seats.map((seat) => nameFor(company, seat)),
                story.points ?? 0,
            );
        case "watching":
            return thinkingCaption(story.seats.map((seat) => nameFor(company, seat)));
    }
}

function listed(names: readonly string[]): string {
    if (names.length <= 1) {
        return names[0] ?? "";
    }
    return `${names.slice(0, -1).join(", ")} and ${names.at(-1) ?? ""}`;
}
