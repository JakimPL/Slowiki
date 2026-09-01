import type { RulesConfig, SettingGroup, SettingName } from "../api/tables";
import type { CompanyView, Tile } from "../api/views";
import type { ScoredWord } from "../play/board/scoring";
import type { Mode } from "../play/device/mode";
import type { Motion } from "../play/device/motion";
import type { Connection } from "../play/live/connection";
import type { Control } from "../play/rules/control";
import type { Deviation } from "../play/rules/deviation";
import type { RulesEntry } from "../play/rules/entry";
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
export const CODE_LABEL = text("arrive.code_label");
export const CREATE_BUTTON = text("arrive.create_button");
export const JOIN_BUTTON = text("arrive.join_button");
export const SWITCH_TO_JOIN = text("arrive.switch_to_join");
export const SWITCH_TO_CREATE = text("arrive.switch_to_create");
export const STALE_NOTICE = text("arrive.stale_notice");
export const JOINING_CAPTION = text("arrive.joining");
export const OFFERINGS_LOADING = text("arrive.offerings_loading");
export const READING_TABLE = text("arrive.reading_table");
export const CODE_HINT = text("arrive.code_hint");
export const RULES_HEADING = text("rules.heading");
export const RULES_CLOSE = text("rules.close");
export const RULES_ROW_LABEL = text("rules.row_label");
export const RULES_STANDARD = text("rules.standard");
export const RULES_REVERT_ALL = text("rules.revert_all");
export const RULES_REVERT = text("rules.revert");
export const RULES_LIMITED = text("rules.limited");
export const RULES_UNLIMITED = text("rules.unlimited");
export const RULES_UNTIMED = text("rules.untimed");
export const RULES_HELP = text("rules.help_label");
export const RULES_CUSTOM = text("rules.custom");
export const RULES_CUSTOM_SPAN = text("rules.custom_span");
export const RULES_STEP_UP = text("rules.step_up");
export const RULES_STEP_DOWN = text("rules.step_down");
export const RULES_EXPERT_LABEL = text("rules.expert_label");
export const RULES_EXPERT_HIDDEN = text("rules.expert_hidden");
export const RULES_EXPERT_SHOWN = text("rules.expert_shown");
export const RULES_SAVED_HEADING = text("rules.saved_heading");
export const RULES_SAVE_LABEL = text("rules.save_label");
export const RULES_SAVE_PLACEHOLDER = text("rules.save_placeholder");
export const RULES_SAVE_BUTTON = text("rules.save_button");
export const RULES_SAVED_NONE = text("rules.saved_none");
export const RULES_DELETE = text("rules.delete");
export const CONFIRM_HEADING = text("rules.confirm_heading");
export const CONFIRM_REVERT = text("rules.confirm_revert");
export const CONFIRM_KEEP = text("rules.confirm_keep");
export const RULES_EXPORT = text("rules.export");
export const RULES_RETIRED = text("rules.retired");
export const LETTERS_HEADING = text("rules.letters_heading");
export const LETTERS_CLOSE = text("rules.letters_close");
export const LETTERS_DONE = text("rules.letters_done");
export const LETTERS_CANCEL = text("rules.letters_cancel");
export const LETTERS_SHUT = text("rules.letters_shut");
export const LETTER_POINTS = text("rules.letter_points");
export const LETTER_COUNT = text("rules.letter_count");
export const LETTER_CATEGORY = text("rules.letter_category");
export const LETTER_BULK_LABEL = text("rules.bulk_label");
export const VALUE_ON = text("rules.value_on");
export const VALUE_OFF = text("rules.value_off");
const CATEGORY_LABELS: Record<string, string> = {
    standard: text("rules.category.standard"),
    yellow: text("rules.category.yellow"),
    green: text("rules.category.green"),
    blue: text("rules.category.blue"),
    red: text("rules.category.red"),
    blank: text("rules.category.blank"),
};
const CHOICE_LABELS: Record<string, string> = {
    first_out: text("rules.choice.first_out"),
    all_out: text("rules.choice.all_out"),
    literaki: text("rules.choice.literaki"),
    "solo-literaki": text("rules.choice.solo-literaki"),
    scrabble: text("rules.choice.scrabble"),
    "scrabble-en": text("rules.choice.scrabble-en"),
    "scrabble-pl": text("rules.choice.scrabble-pl"),
    english: text("rules.choice.english"),
    polish: text("rules.choice.polish"),
    sjp: text("rules.choice.sjp"),
    osps: text("rules.choice.osps"),
};

export function categoryCaption(category: string): string {
    return CATEGORY_LABELS[category] ?? category;
}

export function choiceCaption(choice: string): string {
    return CHOICE_LABELS[choice] ?? choice;
}

export function entryCaption(entry: RulesEntry): string {
    return entry.saved ? entry.label : choiceCaption(entry.label);
}

export const SETTING_LABELS: Record<SettingName, string> = {
    board: text("rules.setting.board"),
    alphabet: text("rules.setting.alphabet"),
    distribution: text("rules.setting.distribution"),
    dictionary: text("rules.setting.dictionary"),
    seats: text("rules.setting.seats"),
    rack_size: text("rules.setting.rack_size"),
    blanks: text("rules.setting.blanks"),
    validate_on_play: text("rules.setting.validate_on_play"),
    premoves: text("rules.setting.premoves"),
    pass_allowed: text("rules.setting.pass_allowed"),
    exchange_limit: text("rules.setting.exchange_limit"),
    exchange_min_bag: text("rules.setting.exchange_min_bag"),
    opening_tiles: text("rules.setting.opening_tiles"),
    opening_covers_center: text("rules.setting.opening_covers_center"),
    bingo_bonus: text("rules.setting.bingo_bonus"),
    bingo_tiles: text("rules.setting.bingo_tiles"),
    ending: text("rules.setting.ending"),
    rack_penalties: text("rules.setting.rack_penalties"),
    going_out_award: text("rules.setting.going_out_award"),
    going_out_bonus: text("rules.setting.going_out_bonus"),
    pass_end_rounds: text("rules.setting.pass_end_rounds"),
    scoreless_end_limit: text("rules.setting.scoreless_end_limit"),
    per_turn_seconds: text("rules.setting.per_turn_seconds"),
    total_seconds: text("rules.setting.total_seconds"),
    increment_seconds: text("rules.setting.increment_seconds"),
    letters: text("rules.setting.letters"),
};
export const SETTING_HELP: Record<SettingName, string> = {
    board: text("rules.help.board"),
    alphabet: text("rules.help.alphabet"),
    distribution: text("rules.help.distribution"),
    dictionary: text("rules.help.dictionary"),
    seats: text("rules.help.seats"),
    rack_size: text("rules.help.rack_size"),
    blanks: text("rules.help.blanks"),
    validate_on_play: text("rules.help.validate_on_play"),
    premoves: text("rules.help.premoves"),
    pass_allowed: text("rules.help.pass_allowed"),
    exchange_limit: text("rules.help.exchange_limit"),
    exchange_min_bag: text("rules.help.exchange_min_bag"),
    opening_tiles: text("rules.help.opening_tiles"),
    opening_covers_center: text("rules.help.opening_covers_center"),
    bingo_bonus: text("rules.help.bingo_bonus"),
    bingo_tiles: text("rules.help.bingo_tiles"),
    ending: text("rules.help.ending"),
    rack_penalties: text("rules.help.rack_penalties"),
    going_out_award: text("rules.help.going_out_award"),
    going_out_bonus: text("rules.help.going_out_bonus"),
    pass_end_rounds: text("rules.help.pass_end_rounds"),
    scoreless_end_limit: text("rules.help.scoreless_end_limit"),
    per_turn_seconds: text("rules.help.per_turn_seconds"),
    total_seconds: text("rules.help.total_seconds"),
    increment_seconds: text("rules.help.increment_seconds"),
    letters: text("rules.help.letters"),
};
export const GROUP_LABELS: Record<SettingGroup, string> = {
    table: text("rules.group.table"),
    words: text("rules.group.words"),
    turns: text("rules.group.turns"),
    scoring: text("rules.group.scoring"),
    letters: text("rules.group.letters"),
};
export const OPEN_SEAT_LABEL = text("seats.open_seat");
export const YOU_MARKER = text("seats.you_marker");
export const OUT_MARKER = text("seats.out_marker");
export const YOUR_TURN_CAPTION = text("seats.your_turn");
export const GAME_OVER_HEADING = text("sheets.game_over_heading");
export const GAME_OVER_VICTORY = text("sheets.game_over_victory");
export const GAME_OVER_UNRESOLVED = text("sheets.game_over_unresolved");
export const UNRESOLVED_CAPTION = text("seats.unresolved");
export const GAME_OVER_CLOSE = text("sheets.game_over_close");
export const TABLE_LEAVE = text("sheets.table_leave");
export const GAME_OVER_DISMISS = text("sheets.game_over_dismiss");
export const MENU_HEADING = text("sheets.menu_heading");
export const MENU_CLOSE = text("sheets.menu_close");
export const MENU_INVITATION = text("sheets.menu_invitation");
export const MENU_LABEL = text("seats.menu_label");
export const MENU_CAPTION = text("seats.menu_caption");
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
export const NOTICE_NOTE = text("seats.notice_note");
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
const SECONDS_PER_HOUR = 3600;
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

export function standingCaption(name: string, rules: RulesConfig): string {
    return counted("arrive.standing", rules.seats, {
        name,
        clock: rules.total_seconds === null ? RULES_UNTIMED : budgetCaption(rules.total_seconds),
    });
}

export function rulesCaption(changes: number): string {
    return changes === 0 ? RULES_STANDARD : counted("rules.changed", changes);
}

export function bagTotalCaption(tiles: number): string {
    return counted("rules.bag_total", tiles);
}

export function confirmDelete(label: string): string {
    return text("rules.confirm_delete", { label });
}

export function standardNote(value: string): string {
    return text("rules.standard_note", { value });
}

export function deviationCaption(deviation: Deviation): string {
    return `${SETTING_LABELS[deviation.setting]} · ${valueCaption(deviation.control)}`;
}

export function valueCaption(control: Control): string {
    switch (control.kind) {
        case "toggle":
            return control.value ? VALUE_ON : VALUE_OFF;
        case "count":
            return String(control.value);
        case "optional_count":
            return control.value === null ? RULES_UNLIMITED : String(control.value);
        case "choice":
            return choiceCaption(control.value);
        case "seconds":
            return control.value === null ? RULES_UNTIMED : budgetCaption(control.value);
        case "letters":
            return text("rules.edited");
    }
}

export function budgetCaption(seconds: number): string {
    const whole = Math.max(0, Math.round(seconds));
    if (whole < SECONDS_PER_MINUTE) {
        return text("clock.seconds", { seconds: whole });
    }
    if (whole < SECONDS_PER_HOUR) {
        return spannedMinutes(whole);
    }
    return spannedHours(whole);
}

function spannedMinutes(whole: number): string {
    const minutes = Math.floor(whole / SECONDS_PER_MINUTE);
    const rest = whole % SECONDS_PER_MINUTE;
    return rest === 0 ? text("clock.minutes", { minutes }) : text("clock.minutes_seconds", { minutes, seconds: rest });
}

function spannedHours(whole: number): string {
    const hours = Math.floor(whole / SECONDS_PER_HOUR);
    const minutes = Math.round((whole % SECONDS_PER_HOUR) / SECONDS_PER_MINUTE);
    return minutes === 0 ? text("clock.hours", { hours }) : text("clock.hours_minutes", { hours, minutes });
}

export function incrementCaption(seconds: number): string {
    return seconds === 0 ? text("clock.increment_none") : text("clock.increment", { span: budgetCaption(seconds) });
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
        case "out-of-time":
            return text("guidance.out_of_time");
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
        case "unresolved":
            return UNRESOLVED_CAPTION;
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
