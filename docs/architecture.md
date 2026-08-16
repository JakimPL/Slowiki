# Architecture

Literabble follows the CardWork architecture: a pure, synchronous game core
surrounded by a transport adapter, game presets, a dictionary subproject, and a
composition root.

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

- `wordcore` — the engine: frozen models, tiles, board, moves, rules kernel,
  lexicon protocol, projections, and the game runner.
- `wordgames` — game presets: shared rules and the literaki/scrabble backends.
- `wordserver` — the FastAPI adapter: tables, sessions, SSE, identity, time.
- `wordtable` — configuration, paths, lexicon service, and CLI entry points.
- `lexica` — dictionary building: word entries, SJP loader, compilation.
- `wordbots` — automated player stubs.

## Vocabulary

- `wordgames.names.GameName` — literaki, scrabble.
- `lexica.names.DictionaryName` — sjp, english, osps.
- `wordcore.moves.action.ActionKind` — play, exchange, pass, reorder.

## Concurrency

The server runs on a single asyncio event loop. Per-table state is guarded by an
`asyncio.Condition` inside `TableSession`; HTTP handlers await, turn timers use
`asyncio.sleep`, and SSE streams wait on the condition. Dictionary compilation
and loading run through `asyncio.to_thread` inside the `LexiconService`, so the
event loop never blocks on disk or CPU-heavy lexicon work.

## Import contracts

`lint-imports` enforces four contracts: the core knows no subsystem, rules are
transport-free, the pure layers reach no adapter or host, and the game,
dictionary, and bot layers stay independent.

`wordserver` consumes configuration and composition helpers from `wordtable`;
a stricter host/adapter split, where `wordtable` is the sole composition root,
is a planned refinement.
