# Dictionaries

## SJP

The SJP game word list lives in `dictionaries/{stem}.zip`, where `{stem}` names
the current release, e.g. `sjp-20260901`.

Archive contents:

- `slowa.txt` — one lowercase Polish word per line, sorted, UTF-8 with CRLF
  line terminators; 3,245,600 lines in `sjp-20260901`. Includes inflected forms.
- `README.txt` — license notice.

License: GPL 2 and Creative Commons Attribution 4.0 International.

Source: <https://sjp.pl/sl/growy/>

`lexica` compiles the archive into `dictionaries/{stem}.words.v1.lexicon`, a
cached artifact the server loads at startup. Every compiled artifact opens with a
header naming its kind and format, and carries both in its filename, so each kind
occupies its own path and a reader accepts only what it understands. `lexica
header <path>` prints that header, and `docs/lexicon-contract.md` holds the kinds,
the envelope and the ownership between `lexica` and `wordtable`. The
`dictionaries/` directory is gitignored.

## Sources

`wordtable fetch` (`make sources`) brings every downloaded source into the
gitignored `dictionaries/` tree: the SJP archive and the PoliMorf table.

**SJP follows the latest release.** sjp.pl publishes one archive at a time, and
<https://sjp.pl/sl/growy/> links the current one. The fetch reads that page, takes
the newest `sjp-YYYYMMDD.zip` it links, downloads it unless it is already on disk,
checks that it is an intact zip holding `slowa.txt`, and writes
`dictionaries/sjp.release.json` with the stem, the URL and the sha256.
`wordtable.paths` reads the stem from that record, so a new release renames the
archive, the compiled artifacts and the coverage diagnostics together. Until a
fetch writes the record, the server offers the SJP games as unavailable.

Every Docker build runs the fetch, and the image picks up a new release on its
next build. Locally, `make sources dictionary rescue coverage` does the same.
`tests/specimens/oracle.yaml` states what Polish grammar requires, so it stands
across releases and moves only when the language does.

**PoliMorf is pinned.** `src/wordtable/sources/releases.py` pins the PoliMorf
table by stem, origin and sha256, and the fetch checks that digest on every run,
also for a file already on disk. To mirror it, copy the pinned file to storage you
control and set `SLOWIKI_SOURCE_MIRROR` to a base URL serving it; the Docker build
takes it as `--build-arg SOURCE_MIRROR=…`.

## Morphology

The Polish morphology pipeline annotates the SJP list with parts of speech and
inflection. `lexica.grammar` holds the closed tagset, one module per dimension,
over a segment table per dialect; `lexica.lore` holds the lexeme identity, the
analysis it carries and the reading the server answers with; `lexica.sources`
reads SGJP and PoliMorf; `lexica.build` groups the analyses; `lexica.maintenance`
holds the overrides and the build manifest. `docs/lore.md` holds the endpoint,
the sources, the measured coverage and the attribution; `docs/morphology.md`
holds the grammar reference and the data-source survey.

## Board layout sources

- Literaki board: recovered from two agreeing open-source implementations
  (`kamilmielnik/scrabble-solver`, `goSciuGH/LiterakiPSk`) and the official
  rules at <https://www.kurnik.pl/literaki/zasady.phtml>.
- Scrabble board: the standard 15×15 premium grid (Wikibooks, Wikipedia).
