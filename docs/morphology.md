# Polish morphology — grammar reference and data sources

This document records the grammatical model `lexica.grammar` encodes and the
survey of data sources that supply complete Polish inflection data. Every
license, format and measurement below comes from a run in this repository.
`docs/lore.md` holds what the running game does with these sources.

## Purpose

The grammar vocabulary lets the game state, for a word in its dictionary:

- a classification into Polish parts of speech (części mowy, Polish
  nomenclature), with grammatical tags for each inflected form,
- the paradigm the form belongs to (deklinacja, koniugacja, stopniowanie),
- the homonymy: one surface form belongs to as many paradigms as Polish gives
  it, and paradigms share forms with each other.

A paradigm groups a lemma, its part of speech and its inflection pattern with
all of its inflected forms, which makes variant recognition the unit of work,
distinct from lemmatization and from stemming.

## Polish grammar reference

### Części mowy

The canonical school set divides into odmienne (inflected) and nieodmienne
(uninflected) parts of speech.

| Polish name | English gloss | Inflected | Inflection kinds |
|---|---|---|---|
| RZECZOWNIK | noun | odmienna | deklinacja: przypadki, liczby, rodzaje |
| PRZYMIOTNIK | adjective | odmienna | deklinacja: przypadki, liczby, rodzaje; stopniowanie |
| LICZEBNIK | numeral | odmienna | deklinacja: przypadki, liczby, rodzaje |
| ZAIMEK | pronoun | odmienna | deklinacja: przypadki, liczby, rodzaje |
| CZASOWNIK | verb | odmienna | koniugacja: osoby, liczby, czasy, tryby, aspekt, rodzaje |
| PRZYSŁÓWEK | adverb | nieodmienna | stopniowanie (partially) |
| PRZYIMEK | preposition | nieodmienna | rekcja (governs a case) |
| SPÓJNIK | conjunction | nieodmienna | — |
| PARTYKUŁA | particle | nieodmienna | — |
| WYKRZYKNIK | interjection | nieodmienna | — |

The pipeline additionally uses `INNY` for tokens outside the canonical ten
(skróty, symbole), so that every dictionary entry carries a label while the
canonical classification stays pure.

### Deklinacja

**Przypadki** (cases), with their traditional questions:

| Case | Polish | Question |
|---|---|---|
| NOM | mianownik | kto? co? |
| GEN | dopełniacz | kogo? czego? |
| DAT | celownik | komu? czemu? |
| ACC | biernik | kogo? co? |
| INST | narzędnik | (z) kim? (z) czym? |
| LOC | miejscownik | (o) kim? (o) czym? |
| VOC | wołacz | o! |

**Liczby**: pojedyncza (sg), mnoga (pl).

**Rodzaje** (genders). The SGJP/Morfeusz tagset uses five:

| Tag | Polish | English |
|---|---|---|
| m1 | męskoosobowy | personal masculine |
| m2 | męskozwierzęcy | animate masculine |
| m3 | męskorzeczowy | inanimate masculine |
| f | żeński | feminine |
| n | nijaki | neuter |

Nouns, adjectives, numerals, and pronouns inflect through all seven cases,
both numbers, and the genders they admit. Nouns additionally carry a
deprecjatywna form (e.g. `chłopy`, `dziady`) for m1 nouns.

### Koniugacja

Verbs inflect through:

- **Osoby**: 1 (pri), 2 (sec), 3 (ter).
- **Liczby**: pojedyncza, mnoga.
- **Czasy**: teraźniejszy (niedokonane only), przeszły, przyszły (prosty for
  dokonane, złożony for niedokonane).
- **Tryby**: oznajmujący (indicative), rozkazujący (imperative),
  przypuszczający (conditional).
- **Aspekt**: dokonany (perf), niedokonany (imperf).
- **Rodzaj**: past-tense forms carry m1/m2/m3/f/n.
- **Formy nieosobowe**:
  - bezokolicznik (infinitive),
  - bezosobnik (-no, -to),
  - imiesłów przymiotnikowy czynny (-ący),
  - imiesłów przymiotnikowy bierny (-ny, -ty),
  - imiesłów przysłówkowy współczesny (-ąc),
  - imiesłów przysłówkowy uprzedni (-łszy, -wszy),
  - odsłownik (rzeczownik odczasownikowy, -nie, -cie).
- **Ruchome końcówki**: bym, byś, by, byśmy, byście (agglutinants attached to
  the conditional mood).

Predykatywy (`trzeba`, `można`, `warto`) are czasowniki niewłaściwe; the
pipeline classifies them as CZASOWNIK with a subtype.

### Stopniowanie

Adjectives and some adverbs inflect through degrees: równy (positive),
wyższy (comparative), najwyższy (superlative). A subset forms degrees
descriptively (bardziej, mniej).

### Liczebniki

Types: główny (cardinal), porządkowy (ordinal), zbiorowy (collective),
ułamkowy (fractional), nieokreślony (indefinite). They inflect through cases,
numbers, and genders.

### Zaimki

Types: osobowy (personal), zwrotny (reflexive: się, siebie), dzierżawczy
(possessive), wskazujący (demonstrative), pytajny (interrogative), względny
(relative), nieokreślony (indefinite), przeczący (negative).

### Przyimki

Przyimki are uninflected; each governs a case (rekcja): biernik, dopełniacz,
celownik, miejscownik, or narzędnik.

## Homonymy

Paradigm-level homonyms share a surface form across distinct paradigms. The
pipeline represents each paradigm as a separate class, so one surface maps to
several classes.

| Surface | Class A | Class B |
|---|---|---|
| bronią | broń, RZECZOWNIK, narzędnik lp f | bronić, CZASOWNIK, 3 os. lm ter. |
| morze / może | morze, RZECZOWNIK, mianownik lp n | móc, CZASOWNIK, 3 os. lp ter. |
| zamek | zamek¹ (budowla), dopełniacz `zamku` | zamek² (błyskawiczny), dopełniacz `zamka` |
| rząd | rząd¹ (władza), dopełniacz `rządu` | rząd² (szereg), dopełniacz `rzędu` |
| bal | bal¹ (belka), dopełniacz `bala` | bal² (zabawa), dopełniacz `balu` |
| marsz | marsz¹ (chód), dopełniacz `marszu` | marsz² (utwór), dopełniacz `marsza` |
| wina | wina¹ (przewinienie) | wino (wina = lm mianownik) |
| drogą | droga, RZECZOWNIK, narzędnik lp | drogi, PRZYMIOTNIK, narzędnik lp f |

Sense homonyms whose paradigms coincide (e.g. `klucz` as wrench and key) share
one class: the class key is lemma + part of speech + inflection pattern, so
identical paradigms merge by construction. Sense-level distinctions (WSJP,
Wiktionary) remain out of scope.

## Data sources

### Ground truth: the SJP game list

`dictionaries/sjp-20260820.zip` contains `slowa.txt`: 3,240,471 lines, one
lowercase Polish word per line, sorted, UTF-8 with CRLF terminators; inflected
forms included. License: GPL 2 and CC BY 4.0. Source: https://sjp.pl/sl/growy/
(verified in this repository, see `docs/dictionaries.md`). The list defines
game validity; morphology annotates it.

### Morfeusz 2 with the SGJP dictionary

A finite-state morphological analyzer from IPI PAN (https://morfeusz.sgjp.pl/).
The bundled dictionary is the Słownik gramatyczny języka polskiego (SGJP) by
Zygmunt Saloni et al., which lists every inflected form of every paradigm
explicitly. The analyzer also generates the full paradigm of a lemma.

Verified in this repository:

- License: the program and the bundled inflectional data (SGJP and PoliMorf
  data) ship under the 2-clause BSD license
  (http://morfeusz.sgjp.pl/doc/license/). The full SGJP text is a separate
  resource with separate terms; the analysis data is BSD-2-Clause.
- Python binding: `morfeusz2` on PyPI, version 1.99.15 (wheel dated
  2026-06-01), cp310-abi3 wheels for Linux, macOS, and Windows.
- Bundled dictionary identity: `pl.sgjp.sgjp-2026.06.01`.
- Output: one tuple per interpretation, `(orth, lemma, tag, names,
  qualifiers)`, e.g. `('bronią', 'broń', 'subst:sg:inst:f', ['nazwa_pospolita'], [])`.
- Homonyms: paradigm-level homonymic lemmas carry pattern-qualified names,
  e.g. `zamek:Sm3~a` (dopełniacz `zamka`) versus `zamek:Sm3~u` (dopełniacz
  `zamku`); usage qualifiers arrive in the qualifiers list (e.g. `muz.`).
- Unrecognized forms yield a single interpretation tagged `ign`.
- Throughput: ≈35,000 forms/s in Python; the full 3,240,471-form pass takes
  ≈91 s in composite mode.
- Coverage: `docs/lore.md` holds the share of the SJP list this source reads.

Role: primary analysis source.

### PoliMorf

A merged inflectional dictionary from ZIL IPI PAN
(https://zil.ipipan.waw.pl/PoliMorf), combining SGJP with further sources.
It ships beside every Morfeusz release. Verified 2026-08-22:

- License: the source data and the resulting resource ship under the
  2-clause BSD license.
- Download: `https://download.sgjp.pl/morfeusz/20260726/polimorf-20260726.tab.gz`;
  45.2 MB compressed, 8,505,529 rows, dictionary id
  `pl.waw.ipipan.polimorf-2026.07.27`, sha256
  `d0315301beb4820577c8e04c885044feb852a72c865ce62e5e0a1836344e078e`.
- Format: a copyright preamble, then five tab-separated columns
  `form<TAB>lemma<TAB>tag<TAB>name<TAB>qualifiers`, e.g.
  `Aalborg<TAB>Aalborg<TAB>subst:sg:nom.acc:m3<TAB>nazwa_geograficzna<TAB>zwykle_lp`.
  A row carries exactly five columns; the preamble carries other arities.
- Tagset: the 2026 SGJP tagset, the same one Morfeusz answers in. All 714
  distinct tags read in `lexica.grammar` under `TagsetDialect.SGJP` with zero
  unmapped segments.
- Homonyms: lemma-level rows merge paradigm-level homonyms (`zamek` has one
  row set, while the 2026 SGJP separates `zamek:Sm3~a` and `zamek:Sm3~u`),
  so a rescued form carries a reading and holds no generated paradigm.
- Coverage: rescues 205,151 of the 543,909 SGJP-unknown forms (37.72%),
  carrying 309,816 (lemma, tag) rows.

Role: supplementary rescue source for SGJP-unknown forms, flagged by source
in the compiled artifact; combined coverage reaches 89.55%.

### Morfologik polish.dict

Binary FSA morphological dictionary for the Java Morfologik library
(https://github.com/morfologik/morfologik-stemming), built from SGJP/PoliMorf
data and used by LanguageTool. The library ships under the BSD-3-Clause
license (verified on GitHub, 2026-08-17). Python consumption requires a reader
for the FSA format; the tabular sources it derives from are preferable.

### WSJP — Wielki słownik języka polskiego PAN

The PAN dictionary (https://wsjp.pl) records full inflection tables per
lexeme. A machine-readable API is reported to exist; the site returned HTTP
403 to plain clients during Phase 0 verification, so endpoint, response
format, bulk-access policy, and license remain to confirm. Role: future
cross-check and sense-level homonym disambiguation.

### Wiktionary PL and kaikki.org

Polish Wiktionary stores per-lemma inflection tables (odmiana templates)
under CC BY-SA. kaikki.org serves machine-readable Wiktionary extracts; the
Polish index exists (https://kaikki.org/dictionary/Polish/, verified
2026-08-17). Role: cross-check and few-shot material for any future review
tool.

### Taggers (cross-check only)

spaCy `pl_core_news_sm/md/lg` (trained on NKJP), KRNNT, and Concraft-pl assign
POS tags to running text. They tag forms; the paradigm sources above enumerate
complete paradigms. Useful as an independent cross-check for disputed
classifications. Licenses: to confirm when a cross-check tool is built.

### Comparison

| Source | Paradigm-complete | Homonyms | Format | Python access | License | Role |
|---|---|---|---|---|---|---|
| SJP słowa.txt | n/a | n/a | plain text | existing loader | GPL 2 + CC BY 4.0 | ground truth |
| Morfeusz 2 / SGJP 2026.06.01 | yes | pattern-qualified lemmas | FSA binary | `morfeusz2` pip | BSD-2-Clause | primary |
| PoliMorf 2026.07.27 | yes | lemma-level (merges paradigms) | tabular text | stdlib | BSD-2-Clause | rescue source |
| Morfologik polish.dict | yes | via source | binary FSA | custom reader | BSD-3-Clause | reference |
| WSJP | yes | senses | API | HTTP | to confirm | future cross-check |
| Wiktionary / kaikki | most | senses | JSONL | stdlib | CC BY-SA | cross-check |
| Taggers (spaCy, KRNNT, Concraft) | no | no | models | pip | to confirm | dispute check |

## Morfeusz tagset → PartOfSpeech mapping (measured)

The mapping is a deterministic table, held by unit tests. Prefixes below come
from a full pass over słowa.txt (3,240,471 forms) in composite mode with the
bundled `pl.sgjp.sgjp-2026.06.01` dictionary. Counts sum the head readings the
pipeline consumes — the interpretations spanning the whole surface — so one
form contributes as many as it carries.

| Tag prefix | PartOfSpeech | Head readings | Notes |
|---|---|---|---|
| subst | RZECZOWNIK | 723,547 | case, number, gender |
| depr | RZECZOWNIK | 10,802 | deprecjatywna forma |
| adj | PRZYMIOTNIK | 1,190,028 | case, number, gender, degree |
| adjp | PRZYMIOTNIK | 6,232 | poprzyimkowy, recorded as a quality |
| adjc | PRZYMIOTNIK | 11 | forma predykatywna (wart, gotów) |
| adv | PRZYSŁÓWEK | 26,136 | degree where present |
| comp | SPÓJNIK | 156 | spójnik podrzędny (by:M, to:M); the conditional clitic is `by:T part` |
| num | LICZEBNIK | 569 | główny; collective forms carry `:col` → ZBIOROWY |
| frag | LICZEBNIK | 90 | fragment of a multiword numeral |
| ppron12, ppron3, siebie | ZAIMEK | 85 | osobowy, zwrotny |
| prep | PRZYIMEK | 166 | governed case |
| conj | SPÓJNIK | 71 | |
| part | PARTYKUŁA | 268 | the 2026 tagset names particles `part` (classic `qub`) |
| interj | WYKRZYKNIK | 378 | |
| fin, bedzie, praet, cond, impt, imps, inf, pcon, pant, pact, ppas, ger | CZASOWNIK | 1,910,480 | verb form, aspect, person, tense; `cond` and a past form carrying its person both arrive in composite mode |
| aglt | CZASOWNIK | 182 | ruchoma końcówka standing on its own |
| winien | CZASOWNIK | 56 | defective verb (winien/powinien) |
| pred | CZASOWNIK | 30 | czasownik niewłaściwy |
| brev | INNY | 24 | skrót |
| romandig | INNY | 3 | Roman numeral |
| ign, xx | INNY | 543,909 | the forms SGJP leaves unread; PoliMorf rescues a share of them |

Liczebniki porządkowe (piąty, drugi) carry the adjective tagset (`adj` with
the lemma qualifier `:A`) and classify as PRZYMIOTNIK; the school-level
ordinal reading is a lemma-level refinement.

## Tag segment inventory (measured)

The closed vocabulary in `lexica.grammar` comes from a full pass over słowa.txt
(3,240,471 forms) in both analyzer modes and over the whole PoliMorf table
(8,505,529 five-field rows). Every distinct tag each source produces parses:
**645** SGJP tags in the composite mode, **576** in the default mode, and
**714** PoliMorf tags under the same 2026 dialect, with zero unrecognised
segments. A segment outside the table refuses the tag and names the dialect.

The 2026 PoliMorf releases answer in the SGJP tagset, so one segment table
serves both sources and `TagsetDialect` carries the single dialect they speak:

| Dimension | SGJP 2026 codes |
|---|---|
| case | nom gen dat acc inst loc voc |
| number | sg pl |
| gender | m1 m2 m3 f n |
| person | pri sec ter |
| aspect | imperf perf |
| degree | pos com sup |
| negation | aff neg |
| quality | akc nakc praep npraep agl nagl wok nwok congr rec col ncol pt pun npun |

Dotted segments state alternatives on one dimension and arrive on every
dimension a source uses them for: `nom.acc.voc` (case), `m1.m2.m3` (gender),
`imperf.perf` (aspect), `akc.nakc` and `congr.rec` and `praep.npraep`
(quality), and **`sg.pl`** (number, 1,540 head readings over nouns and
numerals). Number is therefore a set, as case, gender and aspect already were.

The prefixes `numcomp` and `adja` state the quality ZŁOŻONY on their own, so a
compound-forming numeral and the first member of a compound adjective each read
as złożony without carrying a segment for it.

### Composite past forms (measured, both modes)

`morfeusz2.Morfeusz(praet="composite")` composes the past tense instead of
splitting it into a stem and an agglutinate:

| Reading | Default mode | Composite mode |
|---|---|---|
| praet interpretations | 512,301 | 278,389 |
| aglt interpretations | 282,950 | 182 |
| cond interpretations | — | 233,900 |
| praet carrying a person | none | 278,389 (all) |
| distinct tags | 576 | 645 |

`biegłem` reads as `praet:sg:m1.m2.m3:pri:imperf` with the person restored, and
`zrobiłbym` reads as `cond:sg:m1.m2.m3:pri:perf` — a real conditional, where the
default mode leaves a past form beside a movable ending. The grammar vocabulary
carries both readings: `cond` states the mood PRZYPUSZCZAJĄCY and the verb form
FORMA_PRZYPUSZCZAJĄCA, and `aglt` states the movable ending without claiming a
mood of its own.

### Qualifiers (measured over słowa.txt)

SGJP answers with two vocabularies: **26** name categories (`nazwa_pospolita`
711,277 head readings, `nazwisko` 16,347, `nazwa_geograficzna` 4,180, `imię`
1,323, and 22 rarer ones) and **533** label strings built from **119** atoms
joined by commas (`daw.,char.`). The 2026 PoliMorf shares that vocabulary and
joins with a pipe instead: **35** name atoms across **72** column values
(`imię|nazwisko`) and **596** label values, 43,419 rows of which state several
(`daw.|rzad.`). `lexica.grammar.qualifier` splits on both separators and types
each code as a name or a qualifier.

## Coverage

`docs/lore.md` holds the measured coverage of the SJP list by these sources, the
policy for the forms they leave unread, and the attribution each source
requires.

## Source decision

- Primary analysis source: morfeusz2 with the bundled SGJP 2026.06.01 — newest
  data, paradigm-level homonym separation through pattern-qualified lemmas,
  native paradigm generation.
- Supplementary rescue source: the PoliMorf tabular data for SGJP-unknown
  forms; analyses carry a `source` flag, and the merged lemma-level rows record
  the lower fidelity.
- Both sources ship under the 2-clause BSD license, compatible with the SJP
  list's GPL 2 / CC BY 4.0 terms for the compiled artifacts.
- WSJP and kaikki remain cross-check options; WSJP returned HTTP 403 to plain
  clients.
