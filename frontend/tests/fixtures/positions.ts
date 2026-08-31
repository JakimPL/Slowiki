import type { Offering, RulesConfig, SettingAllowance, TableDescription } from "../../src/api/tables";
import type {
    Board,
    Bonus,
    CompanyView,
    EventView,
    PlayRecord,
    PositionView,
    SeatView,
    TableViewResponse,
    Tile,
} from "../../src/api/views";

export function aTile(overrides: Partial<Tile> = {}): Tile {
    return { identifier: 1, letter: "A", value: 1, category: "yellow", blank: false, ...overrides };
}

export function aBoard(placed: Record<number, Tile> = {}, bonuses: Record<number, Bonus> = {}): Board {
    const size = 15;
    const cells = size * size;
    return {
        size,
        bonuses: Array.from({ length: cells }, (_, index) => bonuses[index] ?? null),
        tiles: Array.from({ length: cells }, (_, index) => placed[index] ?? null),
    };
}

export function aView(overrides: Partial<PositionView> = {}): PositionView {
    return {
        board: aBoard(),
        phase: "turn",
        to_act: [0],
        racks: { 0: [aTile()], 1: null },
        bag_count: 80,
        scores: { 0: 0, 1: 0 },
        exchange_counts: { 0: 0, 1: 0 },
        consecutive_passes: 0,
        scoreless_turns: 0,
        last_play: null,
        premove: null,
        pending_premoves: [],
        turn_number: 0,
        players: [0, 1],
        ...overrides,
    };
}

export function aSeatView(seat: number, overrides: Partial<SeatView> = {}): SeatView {
    return { seat, name: null, claimed: true, connected: false, ...overrides };
}

export function aCompany(seats?: readonly SeatView[]): CompanyView {
    return { seats: [...(seats ?? [aSeatView(0, { name: "Ala" }), aSeatView(1, { name: "Ola" })])] };
}

export function anEvent(overrides: Partial<EventView> = {}): EventView {
    return { seq: 0, kind: "move", actor: 0, move: null, reason: null, position: aView(), ...overrides };
}

export function aPlayRecord(overrides: Partial<PlayRecord> = {}): PlayRecord {
    return {
        player: 0,
        indices: [112, 113],
        words: [{ text: "KO", points: 5 }],
        points: 5,
        bingo: 0,
        turn_number: 0,
        ...overrides,
    };
}

export function someRules(overrides: Partial<RulesConfig> = {}): RulesConfig {
    return {
        board: "literaki",
        alphabet: "literaki",
        distribution: "polish",
        dictionary: "sjp",
        seats: 2,
        rack_size: 7,
        blanks: 2,
        validate_on_play: true,
        premoves: true,
        pass_allowed: true,
        exchange_limit: 3,
        exchange_min_bag: 7,
        opening_tiles: 2,
        opening_covers_center: true,
        bingo_bonus: 50,
        bingo_tiles: null,
        rack_penalties: true,
        going_out_award: true,
        going_out_bonus: 0,
        pass_end_rounds: 2,
        scoreless_end_limit: null,
        per_turn_seconds: null,
        total_seconds: null,
        increment_seconds: 0,
        letters: {},
        ...overrides,
    };
}

export function anOffering(overrides: Partial<Offering> = {}): Offering {
    return {
        name: "literaki",
        specimen: "SŁOWIKI",
        rules: someRules(),
        ...overrides,
    };
}

export function anAllowance(overrides: Partial<SettingAllowance> = {}): SettingAllowance {
    return {
        setting: "seats",
        group: "table",
        tier: "basic",
        kind: "count",
        minimum: 1,
        maximum: 8,
        step: 1,
        unlimited: false,
        offered: null,
        choices: null,
        ...overrides,
    };
}

export function aDescription(overrides: Partial<TableDescription> = {}): TableDescription {
    return {
        code: "KWPZTR",
        scheme: "literaki",
        specimen: "SŁOWIKI",
        rules: someRules(),
        feedback: { word_check: false, lore: true },
        alphabet: [
            { symbol: "A", value: 1, category: "yellow" },
            { symbol: "K", value: 2, category: "green" },
        ],
        distribution: { A: 9, K: 3 },
        blanks: 2,
        ...overrides,
    };
}

export function aTableResponse(overrides: Partial<TableViewResponse> = {}): TableViewResponse {
    return {
        seq: 0,
        view: aView(),
        company: aCompany(),
        clock: null,
        ...overrides,
    };
}
