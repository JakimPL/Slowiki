from collections.abc import Callable, Mapping

from lexica.morph.mapping import morph_tags, part_of_speech
from lexica.morph.models import (
    Analysis,
    ClassRecord,
    MorphTags,
    VariantRecord,
    class_key,
)
from lexica.morph.parts import PartOfSpeech
from lexica.morph.tags import Case, Gender, Number, VerbForm
from wordcore.models.base import BaseFrozen


class ClassStore(BaseFrozen):
    entries: dict[str, tuple[str, ...]]
    classes: dict[str, ClassRecord]
    unknown: tuple[str, ...]


def assemble_classes(
    analyses_by_form: Mapping[str, tuple[Analysis, ...]],
    dictionary: frozenset[str],
    generated_by_lemma: Mapping[str, tuple[tuple[str, str], ...]],
) -> ClassStore:
    class_variants: dict[str, dict[str, set[str]]] = {}
    class_parts: dict[str, PartOfSpeech] = {}
    entry_classes: dict[str, set[str]] = {}
    unknown: list[str] = []

    for form, analyses in analyses_by_form.items():
        if not analyses:
            unknown.append(form)
            continue
        ids: set[str] = set()
        for analysis in analyses:
            class_id = class_key(analysis.lemma, analysis.part)
            class_parts[class_id] = analysis.part
            ids.add(class_id)
            class_variants.setdefault(class_id, {}).setdefault(form, set()).add(analysis.tag)
        entry_classes[form] = ids

    for lemma, generated in generated_by_lemma.items():
        for form, tag in generated:
            class_id = class_key(lemma, part_of_speech(tag))
            if class_id not in class_parts:
                continue
            class_variants.setdefault(class_id, {}).setdefault(form, set()).add(tag)

    classes: dict[str, ClassRecord] = {}
    for class_id, variants in sorted(class_variants.items()):
        part = class_parts[class_id]
        lemma = lexeme_of(class_id[len(part.value) + 1 :])
        base = select_base(part, variants, lexeme_of(lemma))
        records = tuple(
            VariantRecord(form=form, tag=tag, in_dictionary=form in dictionary)
            for form in sorted(variants)
            for tag in sorted(variants[form])
        )
        classes[class_id] = ClassRecord(
            class_id=class_id,
            part=part,
            lemma=lemma,
            base=base,
            variants=records,
        )

    entries = {form: tuple(sorted(ids)) for form, ids in entry_classes.items()}
    return ClassStore(entries=entries, classes=classes, unknown=tuple(unknown))


def lexeme_of(lemma: str) -> str:
    return lemma.split(":", 1)[0]


def select_base(part: PartOfSpeech, variants: dict[str, set[str]], lexeme: str) -> str:
    match part:
        case PartOfSpeech.RZECZOWNIK | PartOfSpeech.LICZEBNIK | PartOfSpeech.ZAIMEK:
            predicate = _is_nominative_singular
        case PartOfSpeech.PRZYMIOTNIK:
            predicate = _is_nominative_singular_masculine
        case PartOfSpeech.CZASOWNIK:
            predicate = _is_infinitive
        case _:
            return lexeme
    form = _matching_form(variants, predicate)
    return form if form is not None else lexeme


def _is_nominative_singular(tags: MorphTags) -> bool:
    return Case.MIANOWNIK in tags.cases and tags.number is Number.POJEDYNCZA


def _is_nominative_singular_masculine(tags: MorphTags) -> bool:
    return (
        Case.MIANOWNIK in tags.cases
        and tags.number is Number.POJEDYNCZA
        and bool(
            tags.genders
            & {
                Gender.MĘSKOOSOBOWY,
                Gender.MĘSKOZWIERZĘCY,
                Gender.MĘSKORZECZOWY,
            }
        )
    )


def _is_infinitive(tags: MorphTags) -> bool:
    return tags.verb_form is VerbForm.BEZOKOLICZNIK


def _matching_form(
    variants: dict[str, set[str]],
    predicate: Callable[[MorphTags], bool],
) -> str | None:
    for form in sorted(variants):
        if any(predicate(morph_tags(tag)) for tag in variants[form]):
            return form
    return None
