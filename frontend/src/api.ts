export interface Offering {
  name: string;
  game: string;
  min_players: number;
  max_players: number;
}

export interface SeatInfo {
  seat: number;
  token: string;
}

export interface TableInfo {
  table_id: string;
  scheme: string;
  game: string;
  seats: SeatInfo[];
}

export interface Bonus {
  kind: string;
  multiplier: number;
  category: string | null;
}

export interface Tile {
  identifier: number;
  letter: string;
  value: number;
  category: string;
  blank: boolean;
}

export interface BoardView {
  size: number;
  bonuses: (Bonus | null)[];
  tiles: (Tile | null)[];
}

export interface PlacementPayload {
  tile_id: number;
  row: number;
  column: number;
  letter: string | null;
}

export type ActionPayload =
  | { kind: "play"; placements: PlacementPayload[] }
  | { kind: "exchange"; tile_ids: number[] }
  | { kind: "pass" };

export interface MovePayload {
  player: number;
  action: ActionPayload;
}

export interface View {
  board: BoardView;
  phase: string;
  to_act: number[];
  racks: Record<string, Tile[] | null>;
  bag_count: number;
  scores: Record<string, number>;
  exchange_counts: Record<string, number>;
  consecutive_passes: number;
  premoves: Record<string, MovePayload | null>;
  turn_number: number;
  players: number[];
}

export interface Style {
  name: string;
  board_color: string;
  text_color: string;
  tile_colors: Record<string, string>;
  premium_colors: Record<string, string>;
}

export interface ViewResponse {
  seq: number;
  style: Style;
  view: View;
}

async function request(path: string, options: RequestInit = {}): Promise<Response> {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body !== null && typeof body.detail === "string" ? body.detail : response.statusText;
    throw new Error(detail);
  }
  return response;
}

export async function fetchOfferings(): Promise<Offering[]> {
  const response = await request("/offerings");
  const body = await response.json();
  return body.offerings as Offering[];
}

export async function createTable(scheme: string, seats: number): Promise<TableInfo> {
  const response = await request("/tables", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scheme, seats }),
  });
  return (await response.json()) as TableInfo;
}

export async function fetchView(tableId: string, token: string): Promise<ViewResponse> {
  const response = await request(`/tables/${tableId}/view`, {
    headers: { "X-Seat-Token": token },
  });
  return (await response.json()) as ViewResponse;
}

export async function submitMove(
  tableId: string,
  token: string,
  move: MovePayload,
  baseSeq: number,
  premove: boolean,
): Promise<number> {
  const response = await request(`/tables/${tableId}/moves`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Seat-Token": token },
    body: JSON.stringify({ move, base_seq: baseSeq, premove }),
  });
  const body = await response.json();
  return body.seq as number;
}
