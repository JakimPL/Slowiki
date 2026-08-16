import { useEffect, useMemo, useState } from "react";
import {
  createTable,
  fetchOfferings,
  fetchView,
  submitMove,
  type MovePayload,
  type Offering,
  type Style,
  type TableInfo,
  type Tile,
  type View,
} from "./api";
import { exchangeMove, passMove, playMove } from "./play";

interface PendingPlacement {
  tileId: number;
  row: number;
  column: number;
  letter: string | null;
}

function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function tokenFor(table: TableInfo, seat: number): string {
  const found = table.seats.find((entry) => entry.seat === seat);
  return found === undefined ? "" : found.token;
}

export function App() {
  const [offerings, setOfferings] = useState<Offering[]>([]);
  const [scheme, setScheme] = useState("literaki");
  const [seatCount, setSeatCount] = useState(2);
  const [table, setTable] = useState<TableInfo | null>(null);
  const [seat, setSeat] = useState(0);
  const [view, setView] = useState<View | null>(null);
  const [style, setStyle] = useState<Style | null>(null);
  const [seq, setSeq] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [pending, setPending] = useState<Record<number, PendingPlacement>>({});
  const [premove, setPremove] = useState(false);

  useEffect(() => {
    void fetchOfferings()
      .then(setOfferings)
      .catch((reason: unknown) => setError(messageOf(reason)));
  }, []);

  useEffect(() => {
    if (table === null) return;
    let active = true;
    const tick = async () => {
      try {
        const data = await fetchView(table.table_id, tokenFor(table, seat));
        if (!active) return;
        setView(data.view);
        setStyle(data.style);
        setSeq(data.seq);
        setError(null);
      } catch (reason) {
        if (active) setError(messageOf(reason));
      }
    };
    void tick();
    const timer = setInterval(tick, 1200);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [table, seat]);

  const ownRack = useMemo(() => {
    if (view === null) return [];
    return view.racks[String(seat)] ?? [];
  }, [view, seat]);

  const rackById = useMemo(
    () => new Map<number, Tile>(ownRack.map((tile) => [tile.identifier, tile])),
    [ownRack],
  );

  const myTurn = view !== null && view.phase === "turn" && view.to_act.includes(seat);

  function startTable() {
    void createTable(scheme, seatCount)
      .then((created) => {
        setTable(created);
        setSeat(created.seats[0]?.seat ?? 0);
        setView(null);
        setPending({});
        setSelected([]);
        setError(null);
      })
      .catch((reason: unknown) => setError(messageOf(reason)));
  }

  function switchSeat(next: number) {
    setSeat(next);
    setSelected([]);
    setPending({});
    setError(null);
  }

  function toggleTile(tileId: number) {
    setSelected((previous) =>
      previous.includes(tileId)
        ? previous.filter((identifier) => identifier !== tileId)
        : [...previous, tileId],
    );
  }

  function placeAt(row: number, column: number, index: number) {
    if (view === null) return;
    const placement = pending[index];
    if (placement !== undefined) {
      const next = { ...pending };
      delete next[index];
      setPending(next);
      setSelected([placement.tileId, ...selected]);
      return;
    }
    const tileId = selected[0];
    if (tileId === undefined || view.board.tiles[index] !== null) return;
    const tile = rackById.get(tileId);
    if (tile === undefined) return;
    let letter: string | null = null;
    if (tile.blank) {
      const answer = window.prompt("letter for blank");
      if (answer === null || answer.trim() === "") return;
      letter = answer.trim().toLowerCase().slice(0, 1);
    }
    setPending({ ...pending, [index]: { tileId, row, column, letter } });
    setSelected(selected.slice(1));
  }

  function clearPending() {
    const returned = Object.values(pending).map((placement) => placement.tileId);
    setPending({});
    setSelected([...returned, ...selected]);
  }

  function send(move: MovePayload, premoveFlag: boolean) {
    if (table === null) return;
    void submitMove(table.table_id, tokenFor(table, seat), move, seq, premoveFlag)
      .then(() => {
        setPending({});
        setSelected([]);
        setError(null);
      })
      .catch((reason: unknown) => setError(messageOf(reason)));
  }

  function play() {
    if (view === null) return;
    const placements = Object.values(pending).map((placement) => ({
      tile_id: placement.tileId,
      row: placement.row,
      column: placement.column,
      letter: placement.letter,
    }));
    send(playMove(seat, placements), premove && !myTurn);
  }

  function exchange() {
    if (selected.length === 0) return;
    send(exchangeMove(seat, selected), false);
  }

  function pass() {
    send(passMove(seat), false);
  }

  if (table === null) {
    return (
      <div className="home">
        <h1>Literabble</h1>
        <label>
          scheme
          <select value={scheme} onChange={(event) => setScheme(event.target.value)}>
            {offerings.map((offering) => (
              <option key={offering.name} value={offering.name}>
                {offering.name} ({offering.game})
              </option>
            ))}
          </select>
        </label>
        <label>
          players
          <input
            type="number"
            min={1}
            max={8}
            value={seatCount}
            onChange={(event) => {
              const parsed = Number(event.target.value);
              setSeatCount(Number.isFinite(parsed) ? parsed : 1);
            }}
          />
        </label>
        <button onClick={startTable}>create table</button>
        {error !== null && <p className="error">{error}</p>}
      </div>
    );
  }

  const size = view === null ? 15 : view.board.size;
  const cells = [];
  if (view !== null && style !== null) {
    for (let row = 0; row < view.board.size; row++) {
      for (let column = 0; column < view.board.size; column++) {
        const index = row * view.board.size + column;
        const serverTile = view.board.tiles[index];
        const placement = pending[index];
        const bonus = view.board.bonuses[index];
        let background = style.board_color;
        let label = "";
        if (bonus !== null) {
          if (bonus.kind === "category_multiplier") {
            background = style.tile_colors[bonus.category ?? ""] ?? background;
          } else if (bonus.kind === "word_multiplier") {
            background = style.premium_colors.word_multiplier;
            label = `${bonus.multiplier}W`;
          } else if (bonus.kind === "letter_multiplier") {
            background = style.premium_colors.letter_multiplier;
            label = `${bonus.multiplier}L`;
          }
        }
        let letter = "";
        let value = 0;
        let tileColor = "";
        if (serverTile !== null) {
          letter = serverTile.letter;
          value = serverTile.value;
          tileColor = style.tile_colors[serverTile.category] ?? "";
        } else if (placement !== undefined) {
          const tile = rackById.get(placement.tileId);
          if (tile !== undefined) {
            letter = placement.letter ?? tile.letter;
            value = tile.value;
            tileColor = style.tile_colors[tile.category] ?? "";
          }
        }
        cells.push(
          <div
            key={index}
            className="cell"
            style={{ backgroundColor: background }}
            onClick={() => placeAt(row, column, index)}
          >
            {serverTile !== null || placement !== undefined ? (
              <div className="tile" style={{ backgroundColor: tileColor }}>
                <span className="letter">{letter}</span>
                {value > 0 && <span className="value">{value}</span>}
              </div>
            ) : (
              <span className="bonus">{label}</span>
            )}
          </div>,
        );
      }
    }
  }

  return (
    <div className="game">
      <header>
        <span className={myTurn ? "turn mine" : "turn"}>{myTurn ? "your turn" : "waiting"}</span>
        <span>bag {view?.bag_count ?? 0}</span>
        <button onClick={() => setTable(null)}>leave</button>
      </header>
      <div className="seats">
        {table.seats.map((entry) => (
          <button
            key={entry.seat}
            className={entry.seat === seat ? "active" : ""}
            onClick={() => switchSeat(entry.seat)}
          >
            seat {entry.seat} ({view?.scores[String(entry.seat)] ?? 0})
          </button>
        ))}
      </div>
      <div className="board" style={{ gridTemplateColumns: `repeat(${size}, 1fr)` }}>
        {cells}
      </div>
      <div className="rack">
        {ownRack.map((tile) => (
          <button
            key={tile.identifier}
            className={selected.includes(tile.identifier) ? "rack-tile selected" : "rack-tile"}
            style={{ backgroundColor: style?.tile_colors[tile.category] ?? "#eeeeee" }}
            onClick={() => toggleTile(tile.identifier)}
          >
            <span className="letter">{tile.blank ? "*" : tile.letter}</span>
            {tile.value > 0 && <span className="value">{tile.value}</span>}
          </button>
        ))}
      </div>
      <div className="controls">
        <button onClick={play} disabled={Object.keys(pending).length === 0}>
          play
        </button>
        <button onClick={exchange} disabled={selected.length === 0}>
          exchange
        </button>
        <button onClick={pass}>pass</button>
        <button onClick={clearPending} disabled={Object.keys(pending).length === 0}>
          recall
        </button>
        <label className="premove">
          <input
            type="checkbox"
            checked={premove}
            onChange={(event) => setPremove(event.target.checked)}
          />
          premove
        </label>
      </div>
      {error !== null && <p className="error">{error}</p>}
    </div>
  );
}
