from collections.abc import Callable, Mapping

from lexica.build.records import ClassRecord, ClassStore, VariantRecord
from lexica.grammar.case import Case
from lexica.grammar.gender import Gender
from lexica.grammar.inflection import Inflection
from lexica.grammar.number import Number
from lexica.grammar.parse import inflection_of
from lexica.grammar.part_of_speech import PartOfSpeech
from lexica.grammar.verb_form import VerbForm
from lexica.lore.analysis import Analysis
from lexica.lore.analysis_source import AnalysisSource, dialect_of
from lexica.lore.lexeme_id import LexemeId, token_of

Reading = tuple[str, AnalysisSource]
Variants = Mapping[str, frozenset[Reading]]
Playable = Callable[[str], bool]

_MASCULINE: frozenset[Gender] = frozenset(
    {
        Gender.MĘSKOOSOBOWY,
        Gender.MĘSKOZWIERZĘCY,
        Gender.MĘSKORZECZOWY,
    }
)


def assemble_classes(
    analyses_by_form: Mapping[str, tuple[Analysis, ...]],
    playable: Playable,
    generated_by_lexeme: Mapping[LexemeId, tuple[tuple[str, str], ...]],
) -> ClassStore:
    variants = _variants(analyses_by_form, generated_by_lexeme)
    classes = {
        lexeme: _class_record(lexeme, forms, playable)
        for lexeme, forms in sorted(variants.items(), key=lambda entry: token_of(entry[0]))
    }
    return ClassStore(
        entries=_entries(analyses_by_form),
        classes=classes,
        unknown=tuple(form for form, analyses in analyses_by_form.items() if len(analyses) == 0),
    )


def select_base(lexeme: LexemeId, variants: Variants) -> str:
    predicate = _base_predicate(lexeme.part)
    if predicate is None:
        return lexeme.lemma
    form = _matching_form(variants, predicate)
    return form if form is not None else lexeme.lemma


def _variants(
    analyses_by_form: Mapping[str, tuple[Analysis, ...]],
    generated_by_lexeme: Mapping[LexemeId, tuple[tuple[str, str], ...]],
) -> dict[LexemeId, dict[str, set[Reading]]]:
    variants: dict[LexemeId, dict[str, set[Reading]]] = {}
    for form, analyses in analyses_by_form.items():
        for analysis in analyses:
            readings = variants.setdefault(analysis.lexeme, {}).setdefault(form, set())
            readings.add((analysis.tag, analysis.source))

    for lexeme, generated in generated_by_lexeme.items():
        if lexeme not in variants:
            continue
        for form, tag in generated:
            variants[lexeme].setdefault(form, set()).add((tag, AnalysisSource.SGJP))

    return variants


def _entries(
    analyses_by_form: Mapping[str, tuple[Analysis, ...]],
) -> dict[str, tuple[LexemeId, ...]]:
    entries: dict[str, tuple[LexemeId, ...]] = {}
    for form, analyses in analyses_by_form.items():
        if len(analyses) == 0:
            continue
        lexemes = {analysis.lexeme for analysis in analyses}
        entries[form] = tuple(sorted(lexemes, key=token_of))
    return entries


def _class_record(
    lexeme: LexemeId,
    forms: Mapping[str, set[Reading]],
    playable: Playable,
) -> ClassRecord:
    variants = {form: frozenset(readings) for form, readings in forms.items()}
    records = tuple(
        VariantRecord(form=form, tag=tag, source=source, in_dictionary=playable(form))
        for form in sorted(variants)
        for tag, source in sorted(variants[form])
    )
    return ClassRecord(
        lexeme=lexeme,
        base=select_base(lexeme, variants),
        variants=records,
    )


def _base_predicate(part: PartOfSpeech) -> Callable[[Inflection], bool] | None:
    match part:
        case PartOfSpeech.RZECZOWNIK | PartOfSpeech.LICZEBNIK | PartOfSpeech.ZAIMEK:
            return _is_nominative_singular
        case PartOfSpeech.PRZYMIOTNIK:
            return _is_nominative_singular_masculine
        case PartOfSpeech.CZASOWNIK:
            return _is_infinitive
        case _:
            return None


def _is_nominative_singular(inflection: Inflection) -> bool:
    return Case.MIANOWNIK in inflection.cases and Number.POJEDYNCZA in inflection.numbers


def _is_nominative_singular_masculine(inflection: Inflection) -> bool:
    return _is_nominative_singular(inflection) and len(inflection.genders & _MASCULINE) > 0


def _is_infinitive(inflection: Inflection) -> bool:
    return inflection.verb_form is VerbForm.BEZOKOLICZNIK


def _matching_form(variants: Variants, predicate: Callable[[Inflection], bool]) -> str | None:
    for form in sorted(variants):
        if any(predicate(inflection_of(tag, dialect_of(source))) for tag, source in variants[form]):
            return form
    return None
