import type { RuleParameters, TableDescription } from "../src/api/tables";
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
} from "../src/api/views";

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

export function someParameters(overrides: Partial<RuleParameters> = {}): RuleParameters {
    return {
        rack_size: 7,
        exchange_limit: 3,
        exchange_min_bag: 7,
        pass_allowed: true,
        bingo_bonus: 50,
        validate_on_play: true,
        premoves_allowed: true,
        pass_end_limit: 2,
        scoreless_end_limit: null,
        time: { per_turn_seconds: null, increment_seconds: 0, total_seconds: null },
        ...overrides,
    };
}

export function aDescription(overrides: Partial<TableDescription> = {}): TableDescription {
    return {
        code: "KWPZTR",
        scheme: "literaki",
        game: "literaki",
        seats: 2,
        dictionary: "sjp",
        parameters: someParameters(),
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
