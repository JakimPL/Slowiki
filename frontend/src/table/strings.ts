import type { CompanyView, Tile } from "../api/views";
import type { ScoredWord } from "../play/board/scoring";
import type { Mode } from "../play/device/mode";
import type { Motion } from "../play/device/motion";
import type { Connection } from "../play/live/connection";
import type { Guidance } from "../play/story/guidance";
import type { HighlightKind } from "../play/story/highlights";
import type { LogEntry } from "../play/story/log";
import type { Story } from "../play/story/story";
import type { ExchangeBlock } from "../play/tiles/exchange";
import type { PremoveKind } from "../play/tiles/premoves";
import type { WordStatus } from "../play/words/feedback";
import { counted, text } from "../text/active";

export const PRODUCT_NAME = text("product.name");
export const PRODUCT_TAGLINE = text("product.tagline");
export const STYLE_FALLBACK_NOTE = text("product.style_fallback");

export const CONNECTION_CAPTIONS: Record<Connection, string> = {
    joining: text("connection.joining"),
    live: text("connection.live"),
    resuming: text("connection.resuming"),
    lost: text("connection.lost"),
};

export const NAME_LABEL = text("arrive.name_label");
export const NAME_PLACEHOLDER = text("arrive.name_placeholder");
export const CREATE_HEADING = text("arrive.create_heading");
export const JOIN_HEADING = text("arrive.join_heading");
export const SCHEME_LABEL = text("arrive.scheme_label");
export const SEATS_LABEL = text("arrive.seats_label");
export const TIME_LABEL = text("arrive.time_label");
export const INCREMENT_LABEL = text("arrive.increment_label");
export const UNTIMED_CAPTION = text("arrive.untimed");
export const CODE_LABEL = text("arrive.code_label");
export const CREATE_BUTTON = text("arrive.create_button");
export const JOIN_BUTTON = text("arrive.join_button");
export const SWITCH_TO_JOIN = text("arrive.switch_to_join");
export const SWITCH_TO_CREATE = text("arrive.switch_to_create");
export const STALE_NOTICE = text("arrive.stale_notice");
export const JOINING_CAPTION = text("arrive.joining");
export const OFFERINGS_LOADING = text("arrive.offerings_loading");
export const OPEN_SEAT_LABEL = text("seats.open_seat");
export const YOU_MARKER = text("seats.you_marker");
export const YOUR_TURN_CAPTION = text("seats.your_turn");
export const GAME_OVER_HEADING = text("sheets.game_over_heading");
export const GAME_OVER_VICTORY = text("sheets.game_over_victory");
export const GAME_OVER_CLOSE = text("sheets.game_over_close");
export const GAME_OVER_LEAVE = text("sheets.game_over_leave");
export const GAME_OVER_DISMISS = text("sheets.game_over_dismiss");
export const HIGHLIGHT_LABELS: Record<HighlightKind, string> = {
    best: text("sheets.highlight_best"),
    longest: text("sheets.highlight_longest"),
    both: text("sheets.highlight_both"),
};
export const STANDING_REOPEN = text("seats.standing_reopen");
export const RETURN_BUTTON = text("arrive.return_button");
export const FORGET_BUTTON = text("arrive.forget_button");
export const INVITE_BUTTON = text("arrive.invite_button");
export const INVITE_COPIED = text("arrive.invite_copied");
export const COPY_CODE_LABEL = text("arrive.copy_code_label");
export const COPIED_MARK = text("arrive.copied_mark");
export const DOCKET_GROUP = "docket";
export const BOARD_LABEL = text("board.label");
export const BOARD_FIT = text("board.fit");
export const BOARD_FIT_LABEL = text("board.fit_label");
export const RACK_LABEL = text("hand.rack_label");
export const PLAY_BUTTON = text("hand.play_button");
export const PREMOVE_BUTTON = text("hand.premove_button");
export const PREMOVE_QUEUED = text("hand.premove_queued");
export const EXCHANGE_QUEUED = text("hand.exchange_queued");
export const CANCEL_PREMOVE = text("hand.cancel_premove");
export const PASS_BUTTON = text("hand.pass_button");
export const RECALL_BUTTON = text("hand.recall_button");
export const SHUFFLE_BUTTON = text("hand.shuffle_button");
export const WORDS_LABEL = text("words.label");
export const TRAY_LABEL = text("hand.tray_label");
export const LOG_LABEL = text("docket.log_label");
export const REMAINING_LABEL = text("docket.remaining_label");
export const PLAYERS_LABEL = text("seats.players_label");
export const BLANK_ROW_MARK = text("docket.blank_row_mark");
export const EMPTY_CLOCK = text("clock.empty");
export const MODE_LABEL = text("seats.mode_label");
export const LOCALE_LABEL = text("seats.locale_label");
export const LOCALE_CAPTION = text("seats.locale_caption");
export const NOTICE_LABEL = text("seats.notice_label");
export const NOTICE_CAPTIONS: Record<"off" | "on", string> = {
    off: text("seats.notice_off"),
    on: text("seats.notice_on"),
};
export const MODE_CAPTIONS: Record<Mode, string> = {
    system: text("seats.mode_system"),
    light: text("seats.mode_light"),
    dark: text("seats.mode_dark"),
};
export const MOTION_LABEL = text("seats.motion_label");
export const MOTION_CAPTIONS: Record<Motion, string> = {
    system: text("seats.motion_system"),
    full: text("seats.motion_full"),
    calm: text("seats.motion_calm"),
};

const SECONDS_PER_MINUTE = 60;
const CLOCK_PAD_WIDTH = 2;
const TERM_SEPARATOR = text("words.term_separator");
export const LIST_SEPARATOR = text("general.list_separator");
const REASON_SEPARATOR = "_";
const REASON_SPACE = " ";

export function clockCaption(seconds: number): string {
    const whole = Math.max(0, Math.floor(seconds));
    const minutes = Math.floor(whole / SECONDS_PER_MINUTE);
    const rest = whole % SECONDS_PER_MINUTE;
    return text("clock.time", { minutes, seconds: String(rest).padStart(CLOCK_PAD_WIDTH, "0") });
}
export const TRAY_HINT = text("hand.tray_hint");
export const PARK_HERE = text("hand.park_here");
export const RETURN_HERE = text("hand.return_here");
export const BLANK_PICKER_HEADING = text("sheets.blank_heading");
export const BLANK_PICKER_CLOSE = text("sheets.blank_close");
export const BLANK_INPUT_LABEL = text("sheets.blank_input_label");
export const BLANK_CONFIRM = text("sheets.blank_confirm");
export const BLANK_TILE_CAPTION = text("hand.blank_tile");
export const WORD_PANEL_CLOSE = text("words.panel_close");
export const WORD_ASKING_NOTE = text("words.asking");
export const WORD_FAILED_NOTE = text("words.failed");
export const WORD_ABSENT_NOTE = text("words.absent");
export const WORD_UNCLASSIFIED_PART = text("words.unclassified_part");
export const WORD_UNCLASSIFIED_NOTE = text("words.unclassified");
export const WORD_SAMPLE_NOTE = text("words.sample");
export const WORD_DEEPEN = text("words.deepen");
export const PARADIGM_BACK = text("words.paradigm_back");
export const PARADIGM_BACK_LABEL = text("words.paradigm_back_label");
export const PARADIGM_GAP = text("words.paradigm_gap");
export const PARADIGM_PLAIN_FORMS = text("words.paradigm_plain_forms");
export const PARADIGM_OTHER_FORMS = text("words.paradigm_other_forms");
export const WORDS_HERE_LABEL = text("words.words_here");

export const WORD_VERDICT_CAPTIONS: Record<WordStatus, string | null> = {
    unknown: null,
    valid: text("words.verdict_valid"),
    invalid: text("words.verdict_invalid"),
    standing: text("words.verdict_standing"),
};

export function wordPanelLabel(word: string): string {
    return text("words.panel_label", { word });
}

export function openWordLabel(word: string): string {
    return text("words.open_word", { word });
}

export function formCaption(form: string): string {
    return form.toLowerCase();
}

export function odmianaCaption(terms: readonly string[]): string {
    return terms.join(TERM_SEPARATOR);
}

export function primaryCaption(premove: boolean, points: number | null): string {
    const base = premove ? PREMOVE_BUTTON : PLAY_BUTTON;
    return points === null ? base : text("hand.primary_scored", { action: base, points });
}

export function budgetCaption(seconds: number): string {
    return text("clock.budget", { minutes: Math.round(seconds / SECONDS_PER_MINUTE) });
}

export function incrementCaption(seconds: number): string {
    return seconds === 0 ? text("clock.increment_none") : text("clock.increment", { seconds });
}

export function exchangeCaption(count: number): string {
    return text("hand.exchange_button", { tiles: count });
}

export function exchangeGuidance(block: ExchangeBlock, remaining: number | null, minBag: number): string {
    if (block === "bag-low") {
        return text("hand.exchange_bag_low", { minimum: minBag });
    }
    if (block === "limit-spent") {
        return text("hand.exchange_spent");
    }
    if (remaining === null) {
        return text("hand.exchange_hint");
    }
    return counted("hand.exchange_left", remaining);
}

export function bingoCaption(bonus: number): string {
    return text("hand.bingo", { bonus });
}

export function queuedCaption(kind: PremoveKind): string {
    return kind === "play" ? PREMOVE_QUEUED : EXCHANGE_QUEUED;
}

export function premoveReturnedCaption(reason: string | null): string {
    if (reason === null) {
        return text("docket.premove_returned");
    }
    return text("docket.premove_returned_reason", { reason: spoken(reason) });
}

export function wordsCaption(words: readonly ScoredWord[]): string {
    return words.map((word) => word.text).join(LIST_SEPARATOR);
}

export function logCaption(entry: LogEntry): string {
    switch (entry.kind) {
        case "play":
            return text("docket.log_play", {
                words: wordsCaption(entry.words),
                points: entry.points ?? 0,
            });
        case "exchange":
            return text("docket.log_exchange");
        case "pass":
            return text("docket.log_pass");
        case "premove-returned":
            return entry.reason === null
                ? text("docket.log_premove_returned")
                : text("docket.log_premove_returned_reason", { reason: spoken(entry.reason) });
    }
}

export function logScoreCaption(points: number): string {
    return text("docket.log_score", { points });
}

export function tileCaption(tile: Tile): string {
    if (tile.blank) {
        return BLANK_TILE_CAPTION;
    }
    return text("hand.tile", { letter: tile.letter, value: tile.value });
}

export function squareCaption(row: number, column: number): string {
    return text("board.square", { row: row + 1, column: column + 1 });
}

export function guidanceCaption(guidance: Guidance): string | null {
    switch (guidance) {
        case null:
            return null;
        case "place":
            return text("guidance.place");
        case "opening-short":
            return text("guidance.opening_short");
        case "off-center":
            return text("guidance.off_center");
        case "detached":
            return text("guidance.detached");
        case "scattered":
            return text("guidance.scattered");
        case "gapped":
            return text("guidance.gapped");
    }
}

export function fallbackNameFor(seat: number): string {
    return text("seats.fallback_name", { seat: seat + 1 });
}

export function nameFor(company: CompanyView, seat: number): string {
    const seated = company.seats.find((candidate) => candidate.seat === seat);
    if (seated?.claimed !== true) {
        return OPEN_SEAT_LABEL;
    }
    return seated.name ?? fallbackNameFor(seat);
}

export function bagCaption(count: number): string {
    return text("docket.bag", { tiles: count });
}

export function offeringCaption(name: string, minimum: number, maximum: number): string {
    const span = minimum === maximum ? String(minimum) : text("arrive.span", { minimum, maximum });
    return counted("arrive.offering", maximum, { name, span });
}

export function gatheringCaption(present: number, total: number): string {
    return text("seats.gathering", { present, total });
}

export function thinkingCaption(names: readonly string[]): string {
    if (names.length === 0) {
        return text("seats.waiting");
    }
    return counted("seats.thinking", names.length, { names: listed(names) });
}

export function wonCaption(names: readonly string[], points: number): string {
    return counted("seats.won", names.length, { names: listed(names), points });
}

export function yourWinCaption(winners: number, points: number): string {
    return counted("seats.won_yours", winners, { points });
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
            return story.mine
                ? yourWinCaption(story.seats.length, story.points ?? 0)
                : wonCaption(
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
    return text("general.list_pair", {
        leading: names.slice(0, -1).join(LIST_SEPARATOR),
        last: names.at(-1) ?? "",
    });
}

function spoken(reason: string): string {
    return reason.replaceAll(REASON_SEPARATOR, REASON_SPACE);
}
