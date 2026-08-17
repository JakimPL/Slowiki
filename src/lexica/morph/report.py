from lexica.morph.index import AnalysisResult
from wordcore.models.base import BaseFrozen


class CoverageReport(BaseFrozen):
    total_forms: int
    classified_sgjp: int
    rescued_polimorf: int
    unknown: int
    class_count: int
    multi_class_forms: int
    max_classes_per_form: int
    classes_per_part: dict[str, int]
    unknown_examples: tuple[str, ...]


def build_report(result: AnalysisResult) -> CoverageReport:
    store = result.store
    classes_per_part: dict[str, int] = {}
    for record in store.classes.values():
        classes_per_part[record.part.value] = classes_per_part.get(record.part.value, 0) + 1

    multi_class_forms = 0
    max_classes_per_form = 0
    for class_ids in store.entries.values():
        count = len(class_ids)
        if count > 1:
            multi_class_forms += 1
        max_classes_per_form = max(max_classes_per_form, count)

    return CoverageReport(
        total_forms=len(store.entries) + len(store.unknown),
        classified_sgjp=result.sgjp_classified,
        rescued_polimorf=result.rescued,
        unknown=len(store.unknown),
        class_count=len(store.classes),
        multi_class_forms=multi_class_forms,
        max_classes_per_form=max_classes_per_form,
        classes_per_part=dict(sorted(classes_per_part.items())),
        unknown_examples=store.unknown[:50],
    )
