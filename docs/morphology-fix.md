# Słownik SJP — diagnoza i plan naprawy

Data: 2026-08-19. Dotyczy podsystemu `lexica` (morfologia: części mowy,
odmiany, homonimy) i artefaktu słownika ładowanego przez grę.

## Metoda `lexica`

Potok przekształca listę słów SJP w skompilowany słownik z morfologią:

1. **Ingest** — `iter_sjp_words` czyta `slowa.txt`, normalizuje do wielkich liter.
2. **Analyse** — `morfeusz2` (słownik SGJP 2026.06.01) analizuje każdą formę;
   formy `ign` ratowane są przez PoliMorf 0.6.7.
3. **Classify** — `mapping.py` mapuje prefiks tagu (`subst`, `fin`, `praet`…)
   na część mowy i tagi gramatyczne.
4. **Assemble** — analizy grupowane są w klasy (lemat + część mowy + wzorzec);
   dla każdej klasy liczone są warianty odmiany i forma bazowa.
5. **Compile** — artefakt v2 (marshal envelope: powierzchnie, indeks
   powierzchnia→klasy, tabela klas, lista UNKNOWN).
6. **Consume** — `wordcore.lexicon.morph.MorphLexicon` odpowiada na
   `judge`/`has_prefix`/`class_infos`/`analysis_rows`.

## Diagnoza

Trzy wady powodują, że output jest nie do przyjęcia.

### 1. Główny artefakt jest uszkodzony i serwer tego nie widzi

`dictionaries/sjp-20260803.v2.lexicon` to **płaska krotka 3 240 429 słów**
(stary format tekstowy), a nie envelope v2. Ładowarka rzuca:

```
InvalidConfiguration: malformed lexicon file
```

Manifest `sjp-20260803.manifest.json` ma digesty zgodne z bieżącymi wejściami,
więc `_compile_sjp` **pomija rekompilację** i serwer ładuje uszkodzony plik.
Prawdziwy artefakt morfologii leży pod `sjp-20260803.morph-v2.lexicon`
(216 MB, poprawny envelope) i **nie jest ładowany** — `dictionary_compiled()`
wskazuje na `.v2.lexicon`.

### 2. Potok ignoruje segmenty morfeusza

`analyse_word_entries` / `analyse_word` biorą każdą interpretację bez patrzenia
na span `(start, end)`. Morfeusz rozbija formy z ruchomą końcówką na segmenty:

```
biegłem = biegł(biec) + em(być, aglt)
```

Efekt — fałszywy lemat `być` przy każdej formie przeszłej/przypuszczającej:

```
BIEGŁEM   -> czasownik:BIEC  +  czasownik:BYĆ
ZROBIŁBYM -> czasownik:BYĆ + czasownik:ZROBIĆ + partykuła:BY:T
```

To jest główne źródło „totalnych bzdur”.

### 3. Kody wzorców SGJP wyciekają do lematów

`KOT:SM1`, `KOT:SM2`, `ZAMEK:SM3~A`, `MOŻE:T`, `MOŻE:I`. Lemat widziany przez
użytkownika powinien być czysty (`kot`, `zamek`, `może`), a wzorzec/qualifier
ma zostać wewnętrznym kluczem.

## Plan naprawy

- **Faza 1 — segmenty:** w `sgjp.py` funkcja `head_interpretations` trzyma
  pełnosłowną interpretację (span `(0, max_end)`), a gdy jej brak — segment
  początkowy (`start == 0`). To obsługuje i `biegłem` (tylko segmenty → `biec`),
  i `czyżby` (pełnosłowna `czyżby` wygrywa nad segmentami `czyż` + `by`).
  Samodzielne `bym`, `byśmy` zostają. Tracona jest osoba przy czasie przeszłym
  (jest w segmencie `aglt`) — akceptowalny kompromis dla słownika gry.
- **Faza 2 — czyste lematy:** `compile.py` i `classes.py` zapisują
  `lexeme_of(lemma)` jako lemat klasy; `class_id` zostaje wewnętrznym kluczem.
- **Faza 3 — artefakt:** `manifest.py` włącza wersję potoku do digestów
  (bump wymusza rekompilację po zmianach kodu); loader rozpoznaje stary płaski
  format i podaje czytelny błąd; rekompilacja do `.v2.lexicon` i usunięcie
  przestarzałych plików.
- **Faza 4 — regresja:** rekompilacja + testy: formy aglutynacyjne bez `być`,
  brak kodów wzorców w lemacie.
