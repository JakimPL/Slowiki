from wordcore.lexicon.morph import MorphLexicon
from wordcore.models.base import BaseFrozen


class LexiconDiff(BaseFrozen):
    surfaces_added: tuple[str, ...]
    surfaces_removed: tuple[str, ...]
    classes_added: tuple[str, ...]
    classes_removed: tuple[str, ...]
    classes_changed: tuple[str, ...]


def diff_lexicons(old: MorphLexicon, new: MorphLexicon) -> LexiconDiff:
    old_surfaces = set(old.surfaces)
    new_surfaces = set(new.surfaces)
    old_classes = old.classes
    new_classes = new.classes

    changed: list[str] = []
    for class_id in sorted(set(old_classes) & set(new_classes)):
        if old_classes[class_id] != new_classes[class_id]:
            changed.append(class_id)

    return LexiconDiff(
        surfaces_added=tuple(sorted(new_surfaces - old_surfaces)),
        surfaces_removed=tuple(sorted(old_surfaces - new_surfaces)),
        classes_added=tuple(sorted(set(new_classes) - set(old_classes))),
        classes_removed=tuple(sorted(set(old_classes) - set(new_classes))),
        classes_changed=tuple(changed),
    )
