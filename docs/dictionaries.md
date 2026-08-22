# Dictionaries

## SJP

The SJP game word list lives in `dictionaries/sjp-20260820.zip`.

Archive contents:

- `slowa.txt` — 3,240,471 lines, one lowercase Polish word per line, sorted,
  UTF-8 with CRLF line terminators. Includes inflected forms.
- `README.txt` — license notice.

License: GPL 2 and Creative Commons Attribution 4.0 International.

Source: <https://sjp.pl/sl/growy/>

`lexica` compiles the archive into `dictionaries/sjp-20260820.words.v1.lexicon`, a
cached artifact the server loads at startup. Every compiled artifact opens with a
header naming its kind and format, and carries both in its filename, so each kind
occupies its own path and a reader accepts only what it understands. `lexica
header <path>` prints that header, and `docs/lexicon-contract.md` holds the kinds,
the envelope and the ownership between `lexica` and `wordtable`. The
`dictionaries/` directory is gitignored.

## Pinned sources

`src/wordtable/releases.py` pins every downloaded source by stem, origin and
sha256 — today the SJP archive and the PoliMorf table. `wordtable fetch`
(`make sources`) downloads each one into the gitignored `dictionaries/` tree and
checks its digest, so the build is a function of the pins. A file already on disk
is checked in place, which turns each pin into a statement about what a developer
already has. `wordtable.paths` derives the artifact stems from the SJP pin, so a
release bump renames the archive, the compiled artifacts and the coverage
diagnostics together.

sjp.pl publishes one archive at a time: <https://sjp.pl/sl/growy/> keeps its
address while the file behind it moves to a new date, and only the current file
stays available. Two habits follow.

**Mirror the pinned archive.** Copy it to storage you control and set
`SLOWIKI_SOURCE_MIRROR` to a base URL serving the pinned file names; the fetch
reads from there and still checks the pinned digests, so the mirror proves itself
on every build. The Docker build takes it as `--build-arg SOURCE_MIRROR=…`.
CC BY 4.0 permits the redistribution, with attribution.

**Follow a new release deliberately.** Read <https://sjp.pl/sl/growy/> for the
current file name, download it, and record its stem and sha256 in `releases.py`.
Then rebuild what moves with the list: the word list, the rescue table, the
coverage report, and `tests/specimens/stress.yaml`.

## Morphology

The Polish morphology pipeline annotates the SJP list with parts of speech and
inflection. `lexica.grammar` holds the closed tagset, one module per dimension,
with a segment table per dialect; `lexica.lore` holds the lexeme identity and
the analysis it carries; `lexica.sources` reads SGJP and PoliMorf;
`lexica.build` groups the analyses; `lexica.maintenance` holds the overrides and
the build manifest. The artifact that carries the annotations into the game is
next. The grammar reference and data-source survey live in
`docs/morphology.md`, the pipeline design in `docs/morphology-pipeline.md`, and
the diagnosis of the defects the first build showed in `docs/morphology-fix.md`.

## Board layout sources

- Literaki board: recovered from two agreeing open-source implementations
  (`kamilmielnik/scrabble-solver`, `goSciuGH/LiterakiPSk`) and the official
  rules at <https://www.kurnik.pl/literaki/zasady.phtml>.
- Scrabble board: the standard 15×15 premium grid (Wikibooks, Wikipedia).
