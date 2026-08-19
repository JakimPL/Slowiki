# The lexicon contract

`lexica` and `wordtable` meet at the compiled dictionary artifact, and this document is
that meeting point. Dictionary work starts here: an artifact kind exists once it holds a
row in the table below, and `make contract` keeps the document and the code in
agreement, both as a pre-commit hook and as a step of `make check`.

## Ownership

- **`lexica` owns the bytes.** It names the kinds, declares the current format of each,
  writes the envelope, and offers one reader per kind. A damaged or foreign artifact
  earns its refusal here, from a message that names the path and states the remedy.
- **`wordtable` owns the placement.** It composes each file name from the kind and the
  format `lexica` declares, builds a missing artifact, caches a loaded one per
  dictionary, and offers the game exactly the capability it asks for.
- **`wordcore` sees a port.** The rules kernel asks a lexicon for a verdict and for a
  prefix; that pair is the whole of what the engine knows about dictionaries.
- **`wordserver` and `wordgames` reach a lexicon through `wordtable`**, by dictionary
  name.

The direction is fixed: `wordtable` imports `lexica`, and `lexica` answers in its own
vocabulary. Where a return type would have to flatten into strings to travel the other
way, the reader belongs in `lexica`.

## Kinds

| Kind | Format | File name | Producer | Reader | Consumer |
| --- | --- | --- | --- | --- | --- |
| `words` | 1 | `{stem}.words.v1.lexicon` | `lexica.artifact.words.write_word_list` | `lexica.artifact.words.read_word_list` | `wordtable.lexicons.load_lexicon` |
| `lore` | 1 | `{stem}.lore.v1.lexicon` | — | — | — |

`words` carries the playable surfaces of one dictionary, sorted and canonically
uppercase, and answers the verdict port.

`lore` carries the augmented lexicon: the readings, paradigms and inflections of each
surface. Its row stands before its producer does, so the path is claimed and a second
builder finds it taken.

An em dash marks a reserved kind: one that owns a name and a format while its code is
still to come.

## Envelope

An artifact opens with a marker, then a four-byte big-endian header length, then a JSON
`ArtifactHeader` carrying the kind, the format and the entry count, then the body. The
header reads on its own, which is what `lexica header <path>` prints and what a
memory-mapped body will want.

| Constant | Value |
| --- | --- |
| `lexica.artifact.envelope.MAGIC` | `LITERABBLE` |
| `lexica.artifact.envelope.LENGTH_BYTES` | `4` |
| `lexica.artifact.envelope.LENGTH_ORDER` | `big` |
| `lexica.artifact.envelope.PARTIAL_SUFFIX` | `.partial` |

A write lands atomically: the bytes go to `<name>.partial`, which is then renamed over
its destination, so an interrupted build leaves the previous artifact in place.

A reader accepts one kind and one format, and states the remedy in every other case:

- a file that opens with other bytes — `carries no artifact header`
- a file that ends inside its header — `ends inside its artifact header`
- a header that fails validation — `carries an unreadable artifact header`
- a kind other than the one the caller asked for — `holds a … artifact where a … artifact belongs`
- a retired format — `holds … format N where format M belongs`
- a body that decodes to another shape — `holds a word list of an unreadable shape`
- an entry count that disagrees with the header — `declares N words and holds M`

## Boundaries

| Boundary | Enforced by |
| --- | --- |
| `lexica` imports no adapter and no host | `Pure layers know no adapter or host` |
| `lexica`, `wordgames` and `wordbots` stay independent | `Game, dictionary, and bot layers stay independent` |
| the engine imports no subsystem | `Core knows no subsystem` |

`lint-imports` holds all three; `make contract` checks that each stays declared in
`pyproject.toml`.

## Changing the contract

- **A new kind** starts as a row here, then reaches `ArtifactKind`, `ARTIFACT_FORMATS`,
  a writer and a reader in `lexica.artifact`, and an accessor in `wordtable`.
- **A new format** for a kind raises the number in `ARTIFACT_FORMATS` and in its row.
  The file name carries the number, so an artifact of the previous format keeps its own
  path and the next build writes beside it.
- **A change to the envelope** updates the constants table together with the code, and
  every existing artifact rebuilds, since the marker and the layout decide whether a
  file reads at all.
