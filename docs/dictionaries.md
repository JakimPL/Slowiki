# Dictionaries

## SJP

The SJP game word list ships in `dictionaries/sjp-20260803.zip`.

Archive contents:

- `slowa.txt` — 3,240,429 lines, one lowercase Polish word per line, sorted,
  UTF-8 with CRLF line terminators. Includes inflected forms.
- `README.txt` — license notice.

License: GPL 2 and Creative Commons Attribution 4.0 International.

Source: <https://sjp.pl/sl/growy/>

`lexica` compiles the archive into `dictionaries/sjp-20260803.words.v1.lexicon`, a
cached artifact the server loads at startup. Every compiled artifact opens with a
header naming its kind and format, and carries both in its filename, so each kind
occupies its own path and a reader accepts only what it understands. `lexica
header <path>` prints that header. The `dictionaries/` directory is gitignored.

## Morphology

The Polish morphology pipeline annotates the SJP list with parts of speech and
inflection classes. `lexica.morph` holds the tagset, the source readers and the
grouping; the artifact that carries the annotations into the game is next. The
grammar reference and data-source survey live in `docs/morphology.md`, the
pipeline design in `docs/morphology-pipeline.md`, and the diagnosis of the
defects the first build showed in `docs/morphology-fix.md`.

## Board layout sources

- Literaki board: recovered from two agreeing open-source implementations
  (`kamilmielnik/scrabble-solver`, `goSciuGH/LiterakiPSk`) and the official
  rules at <https://www.kurnik.pl/literaki/zasady.phtml>.
- Scrabble board: the standard 15×15 premium grid (Wikibooks, Wikipedia).
