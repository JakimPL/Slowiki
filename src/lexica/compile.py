import marshal
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Final, cast

from lexica.morph.classes import lexeme_of, select_base
from lexica.morph.mapping import part_of_speech
from lexica.morph.models import class_key
from lexica.morph.parts import PartOfSpeech
from lexica.morph.sources.polimorf import rescue_rows
from lexica.morph.sources.sgjp import MorfeuszAnalyzer, analyse_word_entries
from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.lexicon.lexicon import TextLexicon
from wordcore.lexicon.morph import MorphClass, MorphLexicon

_ENVELOPE_NAME: Final = "literabble"
_FORMAT: Final = 2
_IGNORED_GENERATION_PREFIXES: Final[frozenset[str]] = frozenset({"ign", "xx"})


def compile_lexicon(words: Iterable[str], destination: Path) -> None:
    surfaces = tuple(sorted({word.upper() for word in words}))
    destination.write_bytes(marshal.dumps((_ENVELOPE_NAME, _FORMAT, surfaces)))


def compile_morph_lexicon(
    words: tuple[str, ...],
    analyzer: MorfeuszAnalyzer,
    polimorf_path: Path | None,
    destination: Path,
    overrides: Mapping[str, tuple[tuple[str, str], ...]] | None = None,
) -> None:
    interned: dict[str, str] = {}
    rows_by_class: dict[str, list[tuple[str, str]]] = {}
    class_parts: dict[str, str] = {}
    class_lemmas: dict[str, str] = {}
    class_sources: dict[str, str] = {}
    entry_classes: dict[str, set[str]] = {}
    unknown: list[str] = []
    overridden_unknown: set[str] = set()
    lemmas_for_generation: dict[str, str] = {}
    overrides_by_form = dict(overrides) if overrides is not None else {}

    def intern(value: str) -> str:
        return interned.setdefault(value, value)

    for word in words:
        override = overrides_by_form.get(word)
        if override is not None:
            if not override:
                unknown.append(word)
                overridden_unknown.add(word)
                continue
            analyses = tuple((lemma, lemma, tag) for (lemma, tag) in override)
        else:
            analyses = analyse_word_entries(analyzer, word.lower())
        if not analyses:
            unknown.append(word)
            continue
        ids: set[str] = set()
        for lemma_upper, lemma_original, tag in analyses:
            part = part_of_speech(tag)
            class_id = class_key(lemma_upper, part)
            class_parts.setdefault(class_id, part.value)
            class_lemmas.setdefault(class_id, lexeme_of(lemma_upper))
            class_sources.setdefault(class_id, "sgjp")
            rows_by_class.setdefault(class_id, []).append((intern(word), intern(tag)))
            ids.add(class_id)
            if override is None:
                lemmas_for_generation[lemma_upper] = lemma_original
        entry_classes[word] = ids

    if polimorf_path is not None and unknown:
        rescue_targets = frozenset(
            word.lower() for word in unknown if word not in overridden_unknown
        )
        rescued = rescue_rows(polimorf_path, rescue_targets)
        still_unknown: list[str] = []
        for word in unknown:
            if word in overridden_unknown:
                still_unknown.append(word)
                continue
            rescued_rows = rescued.get(word.lower())
            if rescued_rows is None:
                still_unknown.append(word)
                continue
            ids = set()
            for lemma, tag in rescued_rows:
                part = part_of_speech(tag)
                class_id = class_key(lemma, part)
                class_parts.setdefault(class_id, part.value)
                class_lemmas.setdefault(class_id, lexeme_of(lemma))
                class_sources.setdefault(class_id, "polimorf")
                rows_by_class.setdefault(class_id, []).append((intern(word), intern(tag)))
                ids.add(class_id)
            entry_classes[word] = ids
        unknown = still_unknown

    for lemma_upper in sorted(lemmas_for_generation):
        lemma_original = lemmas_for_generation[lemma_upper]
        for surface, row_lemma, tag, _, _ in analyzer.generate(lemma_original):
            if row_lemma.upper() != lemma_upper:
                continue
            if tag.split(":", 1)[0] in _IGNORED_GENERATION_PREFIXES:
                continue
            class_id = class_key(lemma_upper, part_of_speech(tag))
            if class_id not in rows_by_class:
                continue
            rows_by_class[class_id].append((intern(surface.upper()), intern(tag)))

    classes: dict[str, tuple[str, str, str, str, tuple[str, ...]]] = {}
    for class_id in sorted(rows_by_class):
        rows = _dedupe_sorted(rows_by_class[class_id])
        variants_by_form: dict[str, set[str]] = {}
        for form, tag in rows:
            variants_by_form.setdefault(form, set()).add(tag)
        part = PartOfSpeech(class_parts[class_id])
        base = select_base(part, variants_by_form, class_lemmas[class_id])
        flat = tuple(piece for pair in rows for piece in pair)
        classes[class_id] = (
            part.value,
            class_lemmas[class_id],
            base,
            class_sources[class_id],
            flat,
        )

    surfaces = tuple(sorted(set(entry_classes) | set(unknown)))
    entries = tuple(tuple(sorted(entry_classes.get(surface, ()))) for surface in surfaces)
    payload = (_ENVELOPE_NAME, _FORMAT, surfaces, entries, classes, tuple(sorted(set(unknown))))
    destination.write_bytes(marshal.dumps(payload))


def load_compiled_lexicon(path: Path) -> TextLexicon | MorphLexicon:
    data = marshal.loads(path.read_bytes())
    if _is_string_tuple(data):
        raise InvalidConfiguration(f"legacy flat lexicon format; recompile the dictionary: {path}")
    if _is_text_payload(data):
        surfaces = data[2]
        if not _is_string_tuple(surfaces):
            raise InvalidConfiguration(f"malformed lexicon file: {path}")
        return TextLexicon(words=surfaces)

    if _is_morph_payload(data):
        surfaces, entries, classes, unknown = data[2], data[3], data[4], data[5]
        if not _is_string_tuple(surfaces) or not _is_string_tuple(unknown):
            raise InvalidConfiguration(f"malformed lexicon file: {path}")
        if not isinstance(entries, tuple) or len(entries) != len(surfaces):
            raise InvalidConfiguration(f"malformed lexicon file: {path}")
        if not all(_is_string_tuple(row) for row in entries):
            raise InvalidConfiguration(f"malformed lexicon file: {path}")
        if not isinstance(classes, dict):
            raise InvalidConfiguration(f"malformed lexicon file: {path}")

        records: dict[str, MorphClass] = {}
        for class_id, record in classes.items():
            fields = _as_class_record(record)
            if not isinstance(class_id, str) or fields is None:
                raise InvalidConfiguration(f"malformed lexicon file: {path}")
            part, lemma, base, source, flat_variants = fields
            records[class_id] = MorphClass(
                class_id=class_id,
                part=part,
                lemma=lemma,
                base=base,
                source=source,
                variants=flat_variants,
            )
        for row in entries:
            for class_id in row:
                if class_id not in records:
                    raise InvalidConfiguration(f"malformed lexicon file: {path}")

        return MorphLexicon(surfaces=surfaces, entries=entries, classes=records, unknown=unknown)

    raise InvalidConfiguration(f"malformed lexicon file: {path}")


def _is_text_payload(data: object) -> bool:
    return (
        isinstance(data, tuple)
        and len(data) == 3
        and data[0] == _ENVELOPE_NAME
        and data[1] == _FORMAT
    )


def _is_morph_payload(data: object) -> bool:
    return (
        isinstance(data, tuple)
        and len(data) == 6
        and data[0] == _ENVELOPE_NAME
        and data[1] == _FORMAT
    )


def _is_string_tuple(value: object) -> bool:
    return isinstance(value, tuple) and all(isinstance(item, str) for item in value)


def _as_class_record(value: object) -> tuple[str, str, str, str, tuple[str, ...]] | None:
    if not isinstance(value, tuple) or len(value) != 5:
        return None
    part, lemma, base, source, flat_variants = value
    if not isinstance(part, str) or not isinstance(lemma, str):
        return None
    if not isinstance(base, str) or not isinstance(source, str):
        return None
    if not _is_string_tuple(flat_variants):
        return None
    return (part, lemma, base, source, cast(tuple[str, ...], flat_variants))


def _dedupe_sorted(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
    rows.sort()
    deduped = [rows[0]]
    for index in range(1, len(rows)):
        if rows[index] != rows[index - 1]:
            deduped.append(rows[index])
    return deduped
