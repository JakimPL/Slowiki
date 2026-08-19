# Dictionaries

## SJP

The SJP game word list ships in `dictionaries/sjp-20260803.zip`.

Archive contents:

- `slowa.txt` — 3,240,429 lines, one lowercase Polish word per line, sorted,
  UTF-8 with CRLF line terminators. Includes inflected forms.
- `README.txt` — license notice.

License: GPL 2 and Creative Commons Attribution 4.0 International.

Source: <https://sjp.pl/sl/growy/>

`lexica` compiles the archive into `dictionaries/sjp-20260803.v2.lexicon`, a cached
morphology artifact the server loads at startup; plain dictionaries compile to
the same format as text-only artifacts. The `dictionaries/` directory is
gitignored.

## Morphology

The planned Polish morphology pipeline annotates the SJP list with parts of
speech and inflection classes. The grammar reference and data-source survey
live in `docs/morphology.md`; the pipeline design (equivalence classes,
homonym handling, artifact v2, incremental re-runs) lives in
`docs/morphology-pipeline.md`.

## Board layout sources

- Literaki board: recovered from two agreeing open-source implementations
  (`kamilmielnik/scrabble-solver`, `goSciuGH/LiterakiPSk`) and the official
  rules at <https://www.kurnik.pl/literaki/zasady.phtml>.
- Scrabble board: the standard 15×15 premium grid (Wikibooks, Wikipedia).
