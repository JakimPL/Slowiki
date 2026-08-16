import type {
    Board,
    Bonus,
    CompanyView,
    EventView,
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

export function aTableResponse(overrides: Partial<TableViewResponse> = {}): TableViewResponse {
    return {
        seq: 0,
        style: {
            name: "default",
            board_color: "#ede5d1",
            text_color: "#2b2419",
            tile_colors: {},
            premium_colors: {},
        },
        view: aView(),
        company: aCompany(),
        ...overrides,
    };
}
