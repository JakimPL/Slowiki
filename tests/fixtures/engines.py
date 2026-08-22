from lexica.lore.rescue import RescueTable
from lexica.lore.sources import LoreSources
from lexica.sources.sgjp import Interpretation


class ScriptedEngine:
    def __init__(
        self,
        answers: dict[str, list[Interpretation]],
        paradigms: dict[str, list[Interpretation]],
    ) -> None:
        self._answers = answers
        self._paradigms = paradigms

    def analyse(self, text: str) -> list[tuple[int, int, Interpretation]]:
        return [(0, 1, interpretation) for interpretation in self._answers.get(text, [])]

    def generate(self, lemma: str) -> list[Interpretation]:
        return self._paradigms.get(lemma, [(lemma, lemma, "ign", [], [])])

    def dict_id(self) -> str:
        return "scripted"


def scripted_sources(
    answers: dict[str, list[Interpretation]],
    paradigms: dict[str, list[Interpretation]],
    rescue: RescueTable,
) -> LoreSources:
    return LoreSources(engine=ScriptedEngine(answers, paradigms), rescue=rescue)
