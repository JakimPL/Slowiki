import type { CompanyView, Tile } from "../api/views";
import type { Connection } from "../play/live/connection";
import type { Guidance } from "../play/story/guidance";
import type { LogEntry } from "../play/story/log";
import type { Story } from "../play/story/story";
import type { ExchangeBlock } from "../play/tiles/exchange";
import type { PremoveKind } from "../play/tiles/premoves";
import type { WordStatus } from "../play/words/feedback";

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
export const TIME_LABEL = "Time per player";
export const INCREMENT_LABEL = "Bonus per move";
export const UNTIMED_CAPTION = "Untimed";
export const CODE_LABEL = "Table code";
export const CREATE_BUTTON = "Start the table";
export const JOIN_BUTTON = "Join the table";
export const SWITCH_TO_JOIN = "Have an invitation code?";
export const SWITCH_TO_CREATE = "Start your own table instead";
export const STALE_NOTICE = "The table has moved on — the latest position is shown.";
export const JOINING_CAPTION = "Joining the table…";
export const OFFERINGS_LOADING = "Reading the table offerings…";
export const OPEN_SEAT_LABEL = "Open seat";
export const YOU_MARKER = "you";
export const YOUR_TURN_CAPTION = "Your turn";
export const GAME_OVER_HEADING = "Game over";
export const INVITE_BUTTON = "Copy invitation";
export const INVITE_COPIED = "Invitation copied";
export const COPY_CODE_LABEL = "Copy the table code";
export const COPIED_MARK = "✓";
export const DOCKET_GROUP = "docket";
export const BOARD_LABEL = "Board";
export const RACK_LABEL = "Your tiles";
export const PLAY_BUTTON = "Play";
export const PREMOVE_BUTTON = "Premove";
export const PREMOVE_QUEUED = "Premove queued";
export const EXCHANGE_QUEUED = "Exchange queued";
export const CANCEL_PREMOVE = "Cancel";
export const PASS_BUTTON = "Pass";
export const RECALL_BUTTON = "Recall";
export const SHUFFLE_BUTTON = "Shuffle";
export const WORDS_LABEL = "Formed words";
export const TRAY_LABEL = "Exchange tray";
export const LOG_LABEL = "Recent moves";
export const REMAINING_LABEL = "Remaining tiles";
export const PLAYERS_LABEL = "Players";
export const BLANK_ROW_MARK = "◇";
export const EMPTY_CLOCK = "—";
export const MODE_LABEL = "Color mode";
export const NOTICE_LABEL = "Notify me when my turn comes while this tab rests";
export const NOTICE_CAPTIONS: Record<"off" | "on", string> = {
    off: "🔔 Off",
    on: "🔔 On",
};
export const MODE_CAPTIONS: Record<"system" | "light" | "dark", string> = {
    system: "◐ Auto",
    light: "○ Light",
    dark: "● Dark",
};

const SECONDS_PER_MINUTE = 60;
const CLOCK_PAD_WIDTH = 2;
const TERM_SEPARATOR = " · ";

export function clockCaption(seconds: number): string {
    const whole = Math.max(0, Math.floor(seconds));
    const minutes = Math.floor(whole / SECONDS_PER_MINUTE);
    const rest = whole % SECONDS_PER_MINUTE;
    return `${String(minutes)}:${String(rest).padStart(CLOCK_PAD_WIDTH, "0")}`;
}
export const TRAY_HINT = "Set tiles aside here to exchange or park them.";
export const PARK_HERE = "Park here";
export const RETURN_HERE = "Return here";
export const BLANK_PICKER_HEADING = "Choose the blank's letter";
export const BLANK_PICKER_CLOSE = "Close the letter picker";
export const BLANK_INPUT_LABEL = "Letter";
export const BLANK_CONFIRM = "Assign the letter";
export const BLANK_TILE_CAPTION = "Blank tile";
export const WORD_PANEL_CLOSE = "Close the word panel";
export const WORD_ASKING_NOTE = "Reading the word…";
export const WORD_FAILED_NOTE = "The word could not be read.";
export const WORD_ABSENT_NOTE = "The dictionary refuses this word, so there is no reading.";
export const WORD_UNCLASSIFIED_PART = "no analysis";
export const WORD_UNCLASSIFIED_NOTE = "The word plays. The morphology sources carry no analysis for it.";
export const WORD_SAMPLE_NOTE = "sample data";
export const WORD_DEEPEN = "Cała odmiana";
export const PARADIGM_BACK = "Back";
export const PARADIGM_BACK_LABEL = "Back to the word card";
export const PARADIGM_GAP = "—";
export const PARADIGM_PLAIN_FORMS = "forms";
export const PARADIGM_OTHER_FORMS = "other forms";

export const WORD_VERDICT_CAPTIONS: Record<WordStatus, string | null> = {
    unknown: null,
    valid: "in the dictionary",
    invalid: "not in the dictionary",
    standing: "standing",
};

export function wordPanelLabel(word: string): string {
    return `${word} — dictionary reading`;
}

export function formCaption(form: string): string {
    return form.toLowerCase();
}

export function odmianaCaption(terms: readonly string[]): string {
    return terms.join(TERM_SEPARATOR);
}

export function primaryCaption(premove: boolean, points: number | null): string {
    const base = premove ? PREMOVE_BUTTON : PLAY_BUTTON;
    return points === null ? base : `${base} · ${String(points)}`;
}

export function budgetCaption(seconds: number): string {
    const minutes = Math.round(seconds / SECONDS_PER_MINUTE);
    return `${String(minutes)} min`;
}

export function incrementCaption(seconds: number): string {
    return seconds === 0 ? "None" : `+${String(seconds)} s`;
}

export function exchangeCaption(count: number): string {
    return `Exchange ${String(count)}`;
}

export function exchangeGuidance(block: ExchangeBlock, remaining: number | null, minBag: number): string {
    if (block === "bag-low") {
        return `Exchanging needs at least ${String(minBag)} tiles left in the bag.`;
    }
    if (block === "limit-spent") {
        return "No exchanges left this game.";
    }
    if (remaining === null) {
        return "Tap Exchange to swap the tray tiles.";
    }
    return `${String(remaining)} ${remaining === 1 ? "exchange" : "exchanges"} left this game.`;
}

export function bingoCaption(bonus: number): string {
    return `Bingo +${String(bonus)}`;
}

export function queuedCaption(kind: PremoveKind): string {
    return kind === "play" ? PREMOVE_QUEUED : EXCHANGE_QUEUED;
}

export function premoveReturnedCaption(reason: string | null): string {
    if (reason === null) {
        return "Premove returned to your rack.";
    }
    return `Premove returned — ${reason.replaceAll("_", " ")}.`;
}

export function logCaption(entry: LogEntry): string {
    switch (entry.kind) {
        case "play":
            return `${entry.words.map((word) => word.text).join(", ")} · ${String(entry.points ?? 0)}`;
        case "exchange":
            return "exchanged tiles";
        case "pass":
            return "passed";
        case "premove-returned":
            return entry.reason === null
                ? "premove returned"
                : `premove returned · ${entry.reason.replaceAll("_", " ")}`;
    }
}

export function tileCaption(tile: Tile): string {
    if (tile.blank) {
        return BLANK_TILE_CAPTION;
    }
    return `Tile ${tile.letter} · ${String(tile.value)}`;
}

export function squareCaption(row: number, column: number): string {
    return `Square ${String(row + 1)}·${String(column + 1)}`;
}

export function guidanceCaption(guidance: Guidance): string | null {
    switch (guidance) {
        case null:
            return null;
        case "place":
            return "Tap an empty square to place the tile.";
        case "opening-short":
            return "The first word needs at least two tiles.";
        case "off-center":
            return "The first word must cross the center star.";
        case "detached":
            return "Connect the word to the tiles on the board.";
        case "scattered":
            return "Keep the word in a single row or column.";
        case "gapped":
            return "Fill every gap in the word.";
    }
}

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
