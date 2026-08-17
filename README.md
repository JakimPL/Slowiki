# Literabble

A configurable Literaki and Scrabble word game for the web.

![Literaki board](docs/media/board-literaki.svg)

## Quickstart

Prerequisites: Python 3.12+, uv, Node.js 20+, npm.

```sh
make install
make build
make serve
```

Open <http://127.0.0.1:8000>, create a table, and share the six-letter join code.
`make build` prepares everything the server needs: the compiled SJP dictionary,
the typed API client, the generated icons and board specimens, and the frontend
bundle. A terminal game runs with `make play`.

The app installs as a PWA from the browser; `docs/mobile.md` records the
Capacitor steps for native iOS and Android shells.

## Configuration

YAML under `config/` is the single authoritative configuration source:

- `config/config.yaml` — service address, active scheme, active style.
- `config/schemes/` — game presets (literaki, scrabble, solo-literaki).
- `config/presets/boards/` — board size and bonus squares.
- `config/presets/tiles/` — letter distributions, values, categories, rack size.
- `config/styles/` — the design tokens (light and dark) for the board, tiles,
  premiums, and chrome.

To add a variant, add a scheme file plus the board and tile files it references.
The offerings endpoint lists a scheme once its dictionary archive is present in
`dictionaries/`; dropping `english.zip` there enables Scrabble.

## Development

`make check` runs the backend gates (pre-commit, mypy, pylint, import contracts,
pytest with coverage). The frontend gates live in `frontend/`: `npm run lint`,
`npm run typecheck`, `npm test`, and `npm run build`; pre-commit runs them for
changed frontend files, and the push hook runs the frontend tests. `make types`
regenerates the typed API client after backend contract changes, and
`make assets` regenerates icons, brand art, and board specimens from the style
tokens.
