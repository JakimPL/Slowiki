from wordcore.errors.exceptions import InvalidConfiguration
from wordcore.tiles.tile import LetterSpec
from wordtable.presets.adjustment import LetterAdjustment
from wordtable.presets.alphabet import AlphabetPreset, LetterClass
from wordtable.presets.distribution import DistributionPreset


def letters_of(
    alphabet: AlphabetPreset,
    distribution: DistributionPreset,
    adjustments: dict[str, LetterAdjustment],
) -> tuple[LetterSpec, ...]:
    counts = distribution.by_symbol()
    _ensure_every_letter_is_counted(alphabet, distribution, counts)
    _ensure_every_count_names_a_letter(alphabet, distribution, counts)
    classes = alphabet.by_symbol()
    ordered = tuple(
        _adjusted(
            _standard(symbol, classes[symbol], counts[symbol]),
            adjustments.get(symbol),
        )
        for symbol in alphabet.order
    )
    return ordered + _added(alphabet, adjustments)


def _standard(symbol: str, letters: LetterClass, count: int) -> LetterSpec:
    return LetterSpec(
        symbol=symbol,
        value=letters.value,
        category=letters.category,
        count=count,
    )


def _adjusted(spec: LetterSpec, adjustment: LetterAdjustment | None) -> LetterSpec:
    if adjustment is None:
        return spec

    return LetterSpec(
        symbol=spec.symbol,
        value=spec.value if adjustment.value is None else adjustment.value,
        category=spec.category if adjustment.category is None else adjustment.category,
        count=spec.count if adjustment.count is None else adjustment.count,
    )


def _added(
    alphabet: AlphabetPreset,
    adjustments: dict[str, LetterAdjustment],
) -> tuple[LetterSpec, ...]:
    ordered = set(alphabet.order)
    return tuple(
        _added_letter(alphabet, symbol, adjustment)
        for symbol, adjustment in adjustments.items()
        if symbol not in ordered
    )


def _added_letter(
    alphabet: AlphabetPreset,
    symbol: str,
    adjustment: LetterAdjustment,
) -> LetterSpec:
    value, category, count = adjustment.value, adjustment.category, adjustment.count
    if value is None or category is None or count is None:
        raise InvalidConfiguration(
            f"alphabet '{alphabet.name}' lacks {symbol}, which then states "
            "a value, a category and a count"
        )

    return LetterSpec(symbol=symbol, value=value, category=category, count=count)


def _ensure_every_letter_is_counted(
    alphabet: AlphabetPreset,
    distribution: DistributionPreset,
    counts: dict[str, int],
) -> None:
    uncounted = "".join(symbol for symbol in alphabet.order if symbol not in counts)
    if uncounted:
        raise InvalidConfiguration(
            f"distribution '{distribution.name}' states no count for {uncounted} "
            f"of alphabet '{alphabet.name}'"
        )


def _ensure_every_count_names_a_letter(
    alphabet: AlphabetPreset,
    distribution: DistributionPreset,
    counts: dict[str, int],
) -> None:
    ordered = set(alphabet.order)
    unknown = "".join(sorted(symbol for symbol in counts if symbol not in ordered))
    if unknown:
        raise InvalidConfiguration(
            f"distribution '{distribution.name}' counts {unknown}, "
            f"which alphabet '{alphabet.name}' lacks"
        )
