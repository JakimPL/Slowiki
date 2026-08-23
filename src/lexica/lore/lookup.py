from lexica.build.assemble import Playable, assemble_classes
from lexica.build.records import ClassRecord, ClassStore, VariantRecord
from lexica.grammar.parse import inflection_of
from lexica.lore.analysis import Analysis
from lexica.lore.analysis_source import dialect_of
from lexica.lore.lexeme_id import token_of
from lexica.lore.override import overridden_analyses
from lexica.lore.reading import InflectedForm, LoreReading, WordLore
from lexica.lore.rescue import rescued_analyses
from lexica.lore.sources import LoreSources
from lexica.sources.paradigms import paradigms_of
from lexica.sources.sgjp import analyse_word
from wordcore.lexicon.protocol import Lexicon


def lore_of(sources: LoreSources, surface: str, lexicon: Lexicon) -> WordLore:
    analyses = analyses_of(sources, surface)
    store = assemble_classes(
        {surface: analyses},
        _playable_in(lexicon),
        paradigms_of(sources.engine, analyses),
    )
    return WordLore(
        word=surface,
        playable=lexicon.judge(surface).allowed,
        readings=_readings_of(store, surface),
    )


def analyses_of(sources: LoreSources, surface: str) -> tuple[Analysis, ...]:
    overridden = sources.overrides.get(surface)
    if overridden is not None:
        return overridden_analyses(surface, overridden)

    analyses = analyse_word(sources.engine, surface)
    if analyses:
        return analyses

    return rescued_analyses(surface, sources.rescue.get(surface, ()))


def _playable_in(lexicon: Lexicon) -> Playable:
    def playable(form: str) -> bool:
        return lexicon.judge(form).allowed

    return playable


def _readings_of(store: ClassStore, surface: str) -> tuple[LoreReading, ...]:
    return tuple(_reading_of(store.classes[lexeme]) for lexeme in store.entries.get(surface, ()))


def _reading_of(record: ClassRecord) -> LoreReading:
    return LoreReading(
        lexeme=token_of(record.lexeme),
        part=record.lexeme.part,
        base=record.base,
        forms=tuple(_form_of(variant) for variant in record.variants),
    )


def _form_of(variant: VariantRecord) -> InflectedForm:
    return InflectedForm(
        text=variant.form,
        tags=inflection_of(variant.tag, dialect_of(variant.source)),
        playable=variant.in_dictionary,
    )
