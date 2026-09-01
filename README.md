# Słowiki

A configurable Literaki/Scrabble-like word game for the web.

![Literaki board](docs/media/board-literaki.svg)

## Quickstart

Prerequisites: Python 3.12+, uv, Node.js 20+, npm.

```sh
make install
make build
make serve
```

Open <http://127.0.0.1:8532>, create a table, and share the six-letter join code.
`make build` prepares everything the server needs: the compiled SJP dictionary,
the typed API client, the generated icons and board specimens, and the frontend
bundle. A terminal game runs with `make play`.

The app installs as a PWA from the browser; `docs/mobile.md` records the
Capacitor steps for native iOS and Android shells.

## Configuration

YAML under `config/` is the single authoritative configuration source:

- `config/config.yaml` — service address, table lifetimes, active scheme, active
  style.
- `config/schemes/` — game presets (literaki, scrabble, scrabble-pl,
  solo-literaki). Each one states its name and a single `rules:` record: which
  board, alphabet, distribution and word list it plays with, how many seats and
  tiles a rack holds, and every rule a table may change.
- `config/allowances.yaml` — what each setting may say and how it is presented:
  the range it takes, the group it joins, how prominent it is, the kind of control
  it takes, and the values a picker offers. One number is authored here and spent
  twice — the server refuses a table outside the range, and the interface offers
  what is inside it.
- `config/presets/boards/` — board size and bonus squares.
- `config/presets/alphabets/` — the letters a game plays with, their order, what
  each class of letters is worth, and the word lists it suits.
- `config/presets/distributions/` — how many tiles of each letter the bag holds.
- `config/styles/` — the design tokens (light and dark) for the board, tiles,
  premiums, and chrome.

To add a variant, add a scheme file plus the board, alphabet, and distribution
files it names. An alphabet and a distribution pair freely: `scrabble-pl` is the
Polish letters at Scrabble values on the Polish distribution, which is a scheme
file and no new letters at all.
The offerings endpoint lists a scheme once its dictionary archive is present in
`dictionaries/`; dropping `english.zip` there enables Scrabble.

The server reads the whole tree at startup and refuses to start on a fault, so a
scheme naming a board that is absent, an alphabet that leaves a letter unvalued,
or a word list its letters do not suit is reported before the first table opens.

## House rules

A scheme is where a table starts, not where it ends. Whoever opens a table can
change any of its rules — the word list, the players, the clock, passing and
exchanging, what earns the bonus, when the game ends and how it is scored, the
board, the letters and how many of each the bag holds — and everyone who joins
reads the changes before taking a seat. The card names how far the rules stand
from the scheme they came from, and the sheet behind it groups the rest so a
standard game needs no decisions at all.

Every rule carries a `?` that says in one sentence what it does. Numbers can be
stepped or simply typed, clocks read in plain spans (`1 min 30 s`), and a table
chooses whether the game ends the moment one player runs out of letters or plays
on until everyone has — along with what the leftover letters are worth and what
finishing first earns.

Rules a player likes are saved on their own device under a name, come back on the
next visit, and can be copied out as text. There are no accounts yet, so they stay
on the device that saved them.

## Deployment

Railway builds and serves the game from the `Dockerfile`: it downloads the SJP
dictionary archive, compiles the lexicon, generates the API client, strings,
and artwork, and builds the frontend bundle. The container runs the game server
on `0.0.0.0` and Railway's `$PORT`, serving the API and the frontend from one
origin. Create a Railway service from the repository; `railway.json` pins the
Dockerfile build and the `/offerings` health check.

## Development

`make check` runs the backend gates (pre-commit, mypy, pylint, import contracts,
pytest with coverage). The frontend gates live in `frontend/`: `npm run lint`,
`npm run typecheck`, `npm test`, and `npm run build`; pre-commit runs them for
changed frontend files, and the push hook runs the frontend tests. `make types`
regenerates the typed API client after backend contract changes, and
`make assets` regenerates icons, brand art, and board specimens from the style
tokens.
