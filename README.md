# Literabble

A configurable Literaki and Scrabble word game for the web.

## Quickstart

Prerequisites: Python 3.12+, uv, Node.js 20+, npm.

```sh
uv sync --all-extras --all-groups
make frontend
make serve
```

Open <http://127.0.0.1:8000>, create a table, and share the six-letter join code.
The first table creation compiles the SJP dictionary into
`dictionaries/sjp-20260803.lexicon`; later runs reuse that artifact. A terminal
game runs with `make play`.

## Configuration

YAML under `config/` is the single authoritative configuration source:

- `config/config.yaml` — service address, active scheme, active style.
- `config/schemes/` — game presets (literaki, scrabble, solo-literaki).
- `config/presets/boards/` — board size and bonus squares.
- `config/presets/tiles/` — letter distributions, values, categories, rack size.
- `config/styles/` — board and tile colors.

To add a variant, add a scheme file plus the board, tile, and style files it
references.
