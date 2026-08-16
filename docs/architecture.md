# Architecture

Literabble follows the CardWork architecture: a pure, synchronous game core
surrounded by a thin transport adapter, game presets, and a composition root.

## Principles

P1. The core is a pure function of the position: `apply(position, move) -> position`.
    Every rule is a pure function of the position it receives.

P2. Randomness is recorded. The bag shuffle is a permutation stored in the
    initial position, so a game replays deterministically.

P3. The board is mechanism, rules are policy. The board stores squares and
    bonuses; the scoring and validity kernel interprets them.

P4. Only projections cross the wire. The server derives a per-observer view and
    hides racks and premoves of other seats.

P5. The journal is append-only. Each move appends a transaction of the form
    `(sequence, move, resulting_position)`.

P6. The engine owns the cursor. Turn order, phase, and premove settlement are
    engine concerns; game rules supply validation and application.

## Packages

- `wordcore` — the engine: models, tiles, board, moves, effects, transactions,
  lexicon, projections, and the game runner.
- `wordgames` — game presets: backend rules and frontend scene data for each game.
- `wordserver` — the FastAPI adapter: rooms, sessions, SSE streams, identity, time.
- `wordtable` — the composition root: configuration, catalogue, hosting, CLI.
- `wordassets` — SVG generation for boards and tiles from style configuration.
- `lexica` — dictionary building: word entries, SJP loader, compilation.
- `wordbots` — automated player stubs.
