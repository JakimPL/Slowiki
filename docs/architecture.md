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

P7. Letters are canonical. Every letter inside the system is uppercase; dictionary
    loaders, tile presets, and move payloads normalize on ingestion, so rules,
    scoring, and projections compare letters directly. Compiled lexicons carry a
    format version (`LEXICON_FORMAT` in `wordtable.paths`), so a normalization
    change retires stale artifacts by filename.

## Packages

- `wordcore` — the engine: frozen models, tiles, board, moves, rules kernel,
  lexicon protocol, projections, and the game runner.
- `wordgames` — game presets: shared rules and the literaki/scrabble backends.
- `wordserver` — the FastAPI adapter: tables, sessions, SSE, identity, time.
- `wordtable` — configuration, paths, lexicon service, and CLI entry points.
- `lexica` — dictionary building: word entries, SJP loader, compilation.
- `wordbots` — automated player stubs.
- `wordassets` — asset generation: an SVG element tree, board specimens, and the
  build CLI writing gitignored `assets/` plus committed specimen copies in
  `docs/media/`.

## Module layout

Each module holds one concept; shared models and enums live in modules named
after them (`board.bonus`, `moves.kind`, `moves.move`, `games.kind`,
`games.rules`, `lexicon.protocol`, `lexicon.verdict`). The rules kernel splits
into `wordcore.rules.words` (placements and word geometry) and
`wordcore.rules.score` (word and move scoring). Dictionary source loaders live
under `lexica.dictionaries`, one module per source.

## Vocabulary

- `wordgames.names.GameName` — literaki, scrabble.
- `lexica.names.DictionaryName` — sjp, english, osps.
- `wordcore.moves.kind.ActionKind` — play, exchange, pass, reorder.
- `wordcore.games.kind.EntryKind` — move, premove_set, premove_cleared,
  premove_discarded.

## HTTP surface

- `GET /offerings` — schemes whose dictionaries are present on disk.
- `GET /style` — the design tokens for the active theme, asked once per client.
- `POST /tables`, `POST /tables/{code}/join` — admissions with seat tokens.
- `GET /tables/{table_id}` — the table description: rules parameters, alphabet,
  distribution, and the join code for seat holders.
- `GET /tables/{table_id}/view` — the per-observer projection with the company
  and the turn clock.
- `GET /tables/{table_id}/words` — dictionary verdicts for up to sixteen words,
  offered while the scheme validates on play (`parameters.word_check`).
- `POST /tables/{table_id}/moves`, `DELETE /tables/{table_id}/premove` — play.
- `GET /tables/{table_id}/events` — the SSE stream: numbered journal frames plus
  unnumbered `presence` and `clock` frames.
- `/artwork` — the generated asset tree (icons, brand art, board specimens);
  `/favicon.ico` serves from it.

## Clocks

Wall-clock time is session state, never position state. `TurnClock`
(`wordserver/clocks.py`) holds what each seat has left and the deadline of the
seat on turn: arming a turn takes the shorter of the scheme's per-turn budget and
the seat's own remaining time, settling a turn charges the thinking time and adds
the increment after a play or an exchange, and a spent budget flags its seat, so
the session auto-passes for it while any opponent still has time. A table asks for
its own control at creation (`TableRequest.time`), which replaces the scheme's
default and rides in the description as `parameters.time`.

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
